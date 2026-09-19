import io, tarfile, zipfile, docker
from extensions import db
from werkzeug.exceptions import Conflict, BadRequest, InternalServerError, NotFound
from models.core.docker import DockerImage

try:
    docker_client = docker.DockerClient(base_url="tcp://ssh-tunnel:2375")
except Exception:
    docker_client = None


def _prepare_tar_from_zip(zip_file_bytes):
    tar_stream = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(zip_file_bytes), 'r') as zf:
        with tarfile.open(fileobj=tar_stream, mode='w') as tf:
            for item in zf.infolist():
                if item.is_dir():
                    continue
                
                file_content = zf.read(item.filename)
                tar_info = tarfile.TarInfo(name=item.filename)
                tar_info.size = len(file_content)
                
                # Droits d'exécution automatiques pour les scripts bash
                if item.filename.endswith('.sh'):
                    tar_info.mode = 0o755
                    
                tf.addfile(tar_info, io.BytesIO(file_content))
    tar_stream.seek(0)
    return tar_stream



def create_docker_image(image_info, zip_file):
    if not docker_client:
        raise InternalServerError("DOCKER_CLIENT_ERROR|Impossible de se connecter au client Docker.")
    name = image_info.get("name")
    tag = (image_info.get("tag") or "latest").strip()
    internal_port = image_info.get("internal_port")
    memory_limit = image_info.get("memory_limit", "256m")
    required_fields = ["name", "internal_port"]
    for field in required_fields:
        if not image_info.get(field):
            raise BadRequest(f"MISSING_FIELD|Le champ '{field}' est obligatoire.")
    # if not isinstance(internal_port, int) or internal_port <= 0:
    #     raise BadRequest("INVALID_INTERNAL_PORT|Le port interne doit être un entier positif.")
    existing_image = DockerImage.query.filter_by(name=name).with_entities(DockerImage.name).first()
    if existing_image:
        raise Conflict("DOCKER_IMAGE_ALREADY_EXISTS|Une image Docker avec ce nom existe déjà.")
    full_image_tag = f"{name}:{tag}"
    try:
        zip_bytes = zip_file.read()
        tar_context = _prepare_tar_from_zip(zip_bytes)

        docker_client.images.build(
            fileobj=tar_context,
            custom_context=True,
            tag=full_image_tag,
            rm=True
        )
        new_image = DockerImage()
        new_image.name = name
        new_image.image_tag = tag
        new_image.internal_port = internal_port
        new_image.memory_limit = memory_limit
        db.session.add(new_image)
        db.session.commit()
        return "Image Docker créée avec succès."
    except zipfile.BadZipFile:
        raise BadRequest("INVALID_ZIP|Le fichier ZIP fourni est invalide ou corrompu.")

    except docker.errors.BuildError as e:
        db.session.rollback()
        log_errors = "".join([line.get('stream', '') for line in e.build_log if 'stream' in line])
        raise InternalServerError(f"DOCKER_BUILD_ERROR|Échec du Build Docker:\n{log_errors}")

    except Exception as e:
        db.session.rollback()
        raise InternalServerError(f"DOCKER_BUILD_ERROR|Erreur lors du build de l'image: {str(e)}")


def modify_docker_image(image_id, image_info):
    if not isinstance(image_id, int) or image_id <= 0:
        raise BadRequest("INVALID_IMAGE_ID|L'ID de l'image doit être un entier positif.")
    image = DockerImage.query.filter_by(id=image_id).first()
    if not image:
        raise NotFound("DOCKER_IMAGE_NOT_FOUND|Image Docker non trouvée.")
    modification = False
    if 'new_image_name' in image_info:
        new_name = image_info['new_image_name']
        if new_name != image.name:
            existing_image = DockerImage.query.filter_by(name=new_name).with_entities(DockerImage.name).first()
            if existing_image:
                raise Conflict("DOCKER_IMAGE_ALREADY_EXISTS|Une image Docker avec ce nom existe déjà.")
            image.name = new_name
            modification = True
    if 'new_image_tag' in image_info:
        new_tag = image_info['new_image_tag']
        if new_tag != image.image_tag:
            image.image_tag = new_tag
            modification = True
    if 'new_internal_port' in image_info:
        new_port = image_info['new_internal_port']
        if not isinstance(new_port, int) or new_port <= 0:
            raise BadRequest("INVALID_INTERNAL_PORT|Le port interne doit être un entier positif.")
        if new_port != image.internal_port:
            image.internal_port = new_port
            modification = True
    if 'new_memory_limit' in image_info:
        new_memory_limit = image_info['new_memory_limit']
        if new_memory_limit != image.memory_limit:
            image.memory_limit = new_memory_limit
            modification = True
    if modification:
        db.session.commit()
        return "Image Docker modifiée avec succès."
    else:
        raise BadRequest("NO_MODIFICATIONS|Aucune modification n'a été apportée à l'image Docker.")

def delete_docker_image(image_id):
    if not isinstance(image_id, int) or image_id <= 0:
        raise BadRequest("INVALID_IMAGE_ID|L'ID de l'image doit être un entier positif.")
    image = DockerImage.query.filter_by(id=image_id).first()
    if not image:
        raise NotFound("DOCKER_IMAGE_NOT_FOUND|Image Docker non trouvée.")
    full_image_tag = f"{image.name}:{image.image_tag}"
    if docker_client:
        try:
            docker_client.images.remove(image=full_image_tag, force=True)
        except docker.errors.ImageNotFound:
            pass
        except docker.errors.APIError as e:
            raise Conflict(f"DOCKER_DELETE_ERROR|Impossible de supprimer l'image sur la VM : {str(e)}")
        except Exception as e:
            raise InternalServerError(f"DOCKER_DELETE_ERROR|Erreur lors de la suppression sur la VM : {str(e)}")
    challenges = image.challenges
    for challenge in challenges:
        challenge.docker_image_id = None
        challenge.hidden = True

    db.session.delete(image)
    db.session.commit()
    return f"Image Docker '{full_image_tag}' supprimée avec succès."

def list_docker_images():
    images = DockerImage.query.all()
    image_list = []
    for image in images:
        image_data = {
            "id": image.id,
            "name": image.name,
            "image_tag": image.image_tag,
            "internal_port": image.internal_port,
            "memory_limit": image.memory_limit,
            "challenge_count": len(image.challenges)
        }
        image_list.append(image_data)
    return image_list

def get_docker_image(image_id):
    if not isinstance(image_id, int) or image_id <= 0:
        raise BadRequest("INVALID_IMAGE_ID|L'ID de l'image doit être un entier positif.")
    image = DockerImage.query.filter_by(id=image_id).first()
    if not image:
        raise NotFound("DOCKER_IMAGE_NOT_FOUND|Image Docker non trouvée.")
    challenge_list = []
    for challenge in image.challenges:
        challenge_data = {
            "id": challenge.id,
            "name": challenge.name,
            "type": challenge.type,
            "category_name": challenge.category.name,
            "is_active": challenge.is_active,
        }
        challenge_list.append(challenge_data)
    image_data = {
        "id": image.id,
        "name": image.name,
        "image_tag": image.image_tag,
        "internal_port": image.internal_port,
        "memory_limit": image.memory_limit,
        "challenge_count": len(image.challenges),
        "challenge_list": challenge_list,
    }
    return image_data
