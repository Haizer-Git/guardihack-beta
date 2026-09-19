import profile
from werkzeug.exceptions import BadRequest, Conflict, InternalServerError, NotFound


from extensions import db
from models.core import (
    UserPreset, PresetToken, User
)

AUTHORIZED_PRESET_TYPES = {
    "USER": True,
    "ADMIN": True,
    "PEDAGOGIE": True,
    "INVITE": True,
    "EXTERNE": True
}

def create_preset(user_id, data):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    if not isinstance(data, dict):
        raise BadRequest("INVALID_DATA|Les données doivent être un dictionnaire.")
    user = User.query.filter_by(id=user_id).with_entities(User.id).first()
    # if not user:
    #     raise NotFound("USER_NOT_FOUND|L'utilisateur créant le preset n'existe pas.")
    required_fields = ['name', 'type', 'affiliation']
    for field in required_fields:
        if not data.get(field):
            raise BadRequest(f"MISSING_{field.upper()}|Le champ '{field}' est requis.")
    if not AUTHORIZED_PRESET_TYPES.get(data['type']):
        raise BadRequest("INVALID_PRESET_TYPE|Le type de preset spécifié n'est pas autorisé.")
    new_preset = UserPreset()
    new_preset.name = data['name']
    new_preset.type = data['type']
    new_preset.affiliation = data['affiliation']
    new_preset.created_by = user_id
    db.session.add(new_preset)
    db.session.commit()
    return f"Preset {new_preset.name} créé avec succès."

def delete_preset(preset_id):
    if not isinstance(preset_id, int):
        raise BadRequest("INVALID_PRESET_ID|L'ID du preset doit être un entier.")
    preset = UserPreset.query.filter_by(id=preset_id).first()
    if not preset:
        raise NotFound("PRESET_NOT_FOUND|Le preset spécifié n'existe pas.")
    PresetToken.query.filter_by(preset_id=preset_id).delete()
    db.session.delete(preset)
    db.session.commit()
    return "Preset supprimé avec succès."

def list_preset():
    presets = UserPreset.query.all()
    result = []
    for p in presets:
        result.append({
            "id": p.id,
            "name": p.name,
            "type": p.type,
            "affiliation": p.affiliation,
            "created_by": p.creator.username if p.creator else None,
            "users_count": len(p.users)
        })
    return result

def get_preset_by_id(preset_id):
    if not isinstance(preset_id, int):
        raise BadRequest("INVALID_PRESET_ID|L'ID du preset doit être un entier.")
    preset = UserPreset.query.filter_by(id=preset_id).first()
    if not preset:
        raise NotFound("PRESET_NOT_FOUND|Le preset spécifié n'existe pas.")
    preset_info = {
        "id": preset.id,
        "name": preset.name,
        "type": preset.type,
        "affiliation": preset.affiliation,
        "created_by": preset.creator.username if preset.creator else None,
        "users_count": len(preset.users)
    }
    return preset_info

def get_admin_preset_users(preset_id):
    if not isinstance(preset_id, int):
        raise BadRequest("INVALID_PRESET_ID|L'ID du preset doit être un entier.")
    preset = UserPreset.query.filter_by(id=preset_id).first()
    if not preset:
        raise NotFound("PRESET_NOT_FOUND|Le preset spécifié n'existe pas.")
    users_data = []
    for u in preset.users:
        users_data.append({
            "id": u.id,
            "username": u.username,
            "mail": u.mail,
            "first_name": u.profile.first_name if u.profile else None,
            "last_name": u.profile.last_name if u.profile else None,
            "classe": u.profile.classe if u.profile else None,
            "niveau": u.profile.niveau if u.profile else None,
            "affiliation": u.profile.affiliation if u.profile else None,
        })
    return users_data