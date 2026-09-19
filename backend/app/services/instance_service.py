import time
from extensions import db
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound, Conflict
from core.instances import (
    create_user_instance, stop_user_instance
)
from models.core import (
    User
)
from models.core.challenge import (
    Challenge
)
from models.core.docker import (
    DockerImage, UserInstance
)

from core.security import (
    generate_user_flag, decrypt_flag
)

def launch_instance_for_user(user_id, challenge_id):
    user = User.query.filter_by(id=user_id).with_entities(User.id, User.secret_key).first()
    if not user:
        raise BadRequest("USER_NOT_FOUND|Utilisateur non trouvé.")
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        raise BadRequest("CHALLENGE_NOT_FOUND|Challenge non trouvé.")
    if challenge.is_active is False:
        raise BadRequest("CHALLENGE_INACTIVE|Le challenge n'est pas actif.")
    active_instance = UserInstance.query.filter_by(user_id=user_id).first()
    if active_instance:
        raise Conflict("INSTANCE_ALREADY_EXISTS|Une instance est déjà active pour cet utilisateur.")
    if challenge.flag_type == "STATIC":
        challenge_flag = decrypt_flag(encrypted_flag=challenge.encrypted_flag)
    elif challenge.flag_type == "DYNAMIC":
        challenge_flag = generate_user_flag(user_secret_key=user.secret_key, challenge_secret_key=challenge.secret_key)
    else:
        raise BadRequest("INVALID_FLAG_TYPE|Type de flag invalide pour ce challenge.")
    challenge_image = challenge.docker_image.name
    internal_port = challenge.docker_image.internal_port
    instance_info = create_user_instance(
        user_id=user_id, 
        challenge_id=challenge_id, 
        challenge_flag=challenge_flag, 
        image_name=challenge_image, 
        internal_port=internal_port
    )
    try:
        new_instance = UserInstance()
        new_instance.container_name = instance_info["container_name"]
        new_instance.subdomain = instance_info["subdomain"]
        new_instance.url = instance_info["url"]
        new_instance.user_id = user_id
        new_instance.challenge_id = challenge_id
        new_instance.expires_at = instance_info["expires_at"]
        db.session.add(new_instance)
        db.session.commit()
        return {
            "url": instance_info["url"],
            "expires_at": instance_info["expires_at"]
        }
    except Exception as e:
        db.session.rollback()
        stop_user_instance(instance_info["container_name"], instance_info["subdomain"])
        raise InternalServerError(f"INSTANCE_SAVE_ERROR|Erreur lors de la sauvegarde de l'instance: {str(e)}")


def stop_instance_for_user(user_id, challenge_id):
    user = User.query.filter_by(id=user_id).with_entities(User.id).first()
    if not user:
        raise BadRequest("USER_NOT_FOUND|Utilisateur non trouvé.")
    challenge = Challenge.query.filter_by(id=challenge_id).with_entities(Challenge.id).first()
    if not challenge:
        raise BadRequest("CHALLENGE_NOT_FOUND|Challenge non trouvé.")
    instance = UserInstance.query.filter_by(user_id=user_id, challenge_id=challenge_id).first()
    if not instance:
        raise NotFound("INSTANCE_NOT_FOUND|Instance non trouvée pour cet utilisateur et ce challenge.")
    stop_user_instance(instance.container_name, instance.subdomain)
    try:
        db.session.delete(instance)
        db.session.commit()
        return "Instance arrêtée avec succès."
    except Exception as e:
        db.session.rollback()
        raise InternalServerError(f"INSTANCE_DELETE_ERROR|Erreur lors de la suppression en base de données: {str(e)}")

def list_instances():
    instances = UserInstance.query.all()
    instance_list = []
    for instance in instances:
        instance_data = {
            "id": instance.id,
            "container_name": instance.container_name,
            "subdomain": instance.subdomain,
            "url": instance.url,
            "user_id": instance.user_id,
            "username": instance.user.username,
            "challenge_id": instance.challenge_id,
            "challenge_name": instance.challenge.name,
            "created_at": instance.created_at.strftime("%d/%m/%Y %H:%M:%S"),
            "expires_at": instance.expires_at.strftime("%d/%m/%Y %H:%M:%S")
        }
        instance_list.append(instance_data)
    return instance_list
