import os, filetype
from werkzeug.exceptions import Conflict, InternalServerError, NotFound, BadRequest
from werkzeug.utils import secure_filename

from extensions import db
from models.core import (
    Icon
)


challenge_file_path = os.getenv('CHALLENGE_FILES_PATH', "./static/challenge_files")
PATHS = {
    "BADGE": os.getenv("BADGES_FILE_PATH", "./static/badges"),
    "AVATAR": os.getenv("AVATAR_FILE_PATH", "./static/cosmetics/avatars"),
    "BANNER": os.getenv("BANNER_FILE_PATH", "./static/cosmetics/banners")
}

AUTHORIZED_ITEM_TYPES = {
    "BADGE": True,
    "AVATAR": True,
    "BANNER": True
}

AUTHORIZED_ICON_EXTENSIONS = {
    "png": True,
    "jpg": True,
    "jpeg": True,
    "gif": True,
    "svg": True
}


def upload_file(challenge_id, file, custom_name=None):
    try:
        challenge_dir = os.path.join(challenge_file_path, f"challenge_files_{challenge_id}")
        if not os.path.exists(challenge_dir):
            os.makedirs(challenge_dir, exist_ok=True)
        head = file.stream.read(2048)
        file.stream.seek(0)
        kind = filetype.guess(head)
        if kind is not None:
            detected_ext = kind.extension
        else:
            detected_ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if custom_name and custom_name.strip():
            clean_custom = custom_name.strip()
            if detected_ext and not clean_custom.lower().endswith(f".{detected_ext}"):
                file_name_final = f"{clean_custom}.{detected_ext}"
            else:
                file_name_final = clean_custom
        else:
            file_name_final = file.filename
        filename = secure_filename(file_name_final)
        file_path = os.path.join(challenge_dir, filename)
        if os.path.exists(file_path):
            raise Conflict("FILENAME_TAKEN|Le nom du fichier est déjà pris")
        file.save(file_path)
        return file_path, (detected_ext or 'bin')
    except Exception as e:
        raise InternalServerError(f"FILE_UPLOAD_ERROR|Erreur lors de l'upload du fichier: {str(e)}")

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    raise NotFound("FILE_NOT_FOUND|Fichier non trouvé pour suppression.")

def upload_icons(files, item_type):
    if not files or not isinstance(files, list):
        raise BadRequest("INVALID_FILES|Aucun fichier fourni ou format invalide.")
    base_path = PATHS.get(item_type)
    if not base_path:
        raise BadRequest(f"INVALID_ITEM_TYPE|Type d'élément invalide: {item_type}.")
    os.makedirs(base_path, exist_ok=True)
    uploaded_icons = []
    for file in files:
        head = file.stream.read(2048)
        file.stream.seek(0)
        kind = filetype.guess(head)
        if kind is not None and AUTHORIZED_ICON_EXTENSIONS.get(kind.extension):
            detected_ext = kind.extension
        else:
            raise BadRequest(f"INVALID_ICON_TYPE|Le fichier '{file.filename}' n'a pas un format valide (PNG, JPG, JPEG, GIF, SVG).")
        filename = secure_filename(file.filename)
        if not filename.lower().endswith(f".{detected_ext}"):
            filename = f"{filename}.{detected_ext}"
        file_path = os.path.join(base_path, filename)
        if os.path.exists(file_path):
            raise Conflict(f"FILENAME_TAKEN|Le nom de fichier '{filename}' est déjà pris.")
        file.save(file_path)
        new_icon = Icon()
        new_icon.filename = filename
        new_icon.filepath = file_path
        new_icon.filetype = item_type
        db.session.add(new_icon)
        uploaded_icons.append(new_icon)
    db.session.commit()
    return len(uploaded_icons)

def delete_icon(icon_id):
    if not isinstance(icon_id, int):
        raise BadRequest("INVALID_ICON_ID|L'ID de l'icône doit être un entier.")
    icon = Icon.query.filter_by(id=icon_id).first()
    if not icon:
        raise NotFound("ICON_NOT_FOUND|Icône non trouvée.")
    if icon.badges or icon.avatars or icon.banners:
        raise Conflict("ICON_IN_USE|L'icône est actuellement utilisée et ne peut pas être supprimée.")
    if os.path.exists(icon.filepath):
        os.remove(icon.filepath)
    db.session.delete(icon)
    db.session.commit()
    return f"L'icône avec l'ID {icon_id} a été supprimée avec succès."

def get_all_icons(item_type=None):
    if item_type and not AUTHORIZED_ITEM_TYPES.get(item_type):
        raise BadRequest(f"INVALID_ITEM_TYPE|Type d'élément invalide: {item_type}.")
    query = Icon.query
    if item_type:
        query = query.filter_by(filetype=item_type)
    icons = query.all()
    return [
        {
            "id": icon.id,
            "filename": icon.filename,
            "filepath": icon.filepath,
            "filetype": icon.filetype,
            "uploaded_at": icon.created_at.strftime("%d/%m/%Y %H:%M:%S") if icon.created_at else None
        } for icon in icons
    ]