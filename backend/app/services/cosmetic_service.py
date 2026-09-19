from numpy import random

from extensions import db
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import Conflict, Forbidden, NotFound, BadRequest, InternalServerError
from models.core import (
    Cosmetic, UserCosmetic, User, 
    UserProfile, Icon
)

AUTHORIZED_COSMETICS_TYPES = {
    "AVATAR": True, 
    "BANNER": True
}

AUTHORIZED_REQUIREMENTS = {
    "CHALLENGE_ID": True,
    "SOLVE_COUNT": True,
    "SCORE": True,
    "CATEGORY_SOLVE_COUNT": True,
    "CONNECTION_STREAK": True,
    "CONNECTION_DATE": True
}

AUTHORIZED_RARETE = {
    "COMMUN": True,
    "RARE": True,
    "EPIC": True,
    "LEGENDARY": True
}


def create_cosmetic(user_id, cosmetic_info):
    required_fields = ['name', 'description', 'type', 'icon_id', 'rarete', 'exclu']
    for field in required_fields:
        if field not in cosmetic_info or cosmetic_info.get(field) is None:
            raise BadRequest(f"MISSING_FIELD|Le champ '{field}' est requis pour créer un cosmétique.")
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    if not isinstance(cosmetic_info, dict):
        raise BadRequest("INVALID_COSMETIC_DATA|Les informations du cosmétique doivent être sous forme de dictionnaire.")
    user = User.query.filter_by(id=user_id).with_entities(User.id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|L'utilisateur créant le cosmétique n'existe pas.")
    name = cosmetic_info['name']
    description = cosmetic_info['description']
    cosmetic_type = cosmetic_info['type']
    rarete = cosmetic_info['rarete']
    exclu = cosmetic_info['exclu']
    icon_id = cosmetic_info["icon_id"]
    if not isinstance(icon_id, int):
        raise BadRequest("INVALID_ICON_ID|L'ID de l'icône doit être un entier.")
    icons = Icon.query.filter_by(id=icon_id).with_entities(Icon.id).first()
    if not icons:
        raise NotFound("ICON_NOT_FOUND|L'icône spécifiée n'existe pas.")
    if not isinstance(exclu, bool):
        raise BadRequest("INVALID_EXCLU_VALUE|La valeur de l'exclusivité doit être un booléen.")
    if not AUTHORIZED_COSMETICS_TYPES.get(cosmetic_type):
        raise BadRequest("INVALID_COSMETIC_TYPE|Type de cosmétique invalide.")
    if not AUTHORIZED_RARETE.get(rarete):
        raise BadRequest("INVALID_RARETE|Rareté invalide.")
    cosmetics = Cosmetic.query.filter_by(name=name).with_entities(Cosmetic.id).first() is not None
    if cosmetics:
        raise Conflict("COSMETIC_ALREADY_EXISTS|Un cosmétique avec ce nom existe déjà.")
    new_cosmetic = Cosmetic(
        type=cosmetic_type,
        name=name,
        description=description,
        icon_id=icon_id,
        rarete=rarete,
        exclu=exclu,
        created_by=user_id
    )
    db.session.add(new_cosmetic)
    db.session.commit()
    return f"Le cosmétique {name} a été créé avec succès."

def modify_cosmetic(cosmetic_id, cosmetic_info):
    if not isinstance(cosmetic_id, int):
        raise BadRequest("INVALID_COSMETIC_ID|L'ID du cosmétique doit être un entier.")
    if not isinstance(cosmetic_info, dict):
        raise BadRequest("INVALID_COSMETIC_DATA|Les informations doivent être sous forme de dictionnaire.")
    cosmetic = Cosmetic.query.filter_by(id=cosmetic_id).first()
    if not cosmetic:
        raise NotFound("COSMETIC_NOT_FOUND|Cosmétique non trouvé.")
    modification = False
    if 'new_name' in cosmetic_info:
        new_name = cosmetic_info['new_name']
        name_exists = Cosmetic.query.filter(Cosmetic.name == new_name, Cosmetic.id != cosmetic_id).with_entities(Cosmetic.id).first()
        if name_exists:
            raise Conflict("COSMETIC_ALREADY_EXISTS|Un cosmétique avec ce nom existe déjà.")
        cosmetic.name = new_name
        modification = True
    if 'new_description' in cosmetic_info:
        cosmetic.description = cosmetic_info['new_description']
        modification = True
    if 'new_type' in cosmetic_info:
        new_type = cosmetic_info['new_type']
        if not AUTHORIZED_COSMETICS_TYPES.get(new_type):
            raise BadRequest("INVALID_COSMETIC_TYPE|Type de cosmétique invalide.")
        cosmetic.type = new_type
        modification = True
    if 'new_icon_id' in cosmetic_info:
        new_icon_id = cosmetic_info['new_icon_id']
        if not isinstance(new_icon_id, int):
            raise BadRequest("INVALID_ICON_ID|L'ID de l'icône doit être un entier.")
        icon = Icon.query.filter_by(id=new_icon_id).with_entities(Icon.id).first()
        if not icon:
            raise NotFound("ICON_NOT_FOUND|L'icône spécifiée n'existe pas.")
        cosmetic.icon_id = new_icon_id
        modification = True
    if 'new_rarete' in cosmetic_info:
        new_rarete = cosmetic_info['new_rarete']
        if not AUTHORIZED_RARETE.get(new_rarete):
            raise BadRequest("INVALID_RARETE|Rareté invalide.")
        cosmetic.rarete = new_rarete
        modification = True
    if 'new_exclu' in cosmetic_info:
        if not isinstance(cosmetic_info['new_exclu'], bool):
            raise BadRequest("INVALID_EXCLU_VALUE|La valeur de l'exclusivité doit être un booléen.")
        cosmetic.exclu = cosmetic_info['new_exclu']
        modification = True
    if modification:
        db.session.commit()
        return f"Le cosmétique {cosmetic.name} a été modifié avec succès."
    else : 
        raise BadRequest("NO_MODIFICATIONS|Aucune modification n'a été apportée au cosmétique.")

def delete_cosmetic(cosmetic_id):
    if not isinstance(cosmetic_id, int):
        raise BadRequest("INVALID_COSMETIC_ID|L'ID du cosmétique doit être un entier.")
    cosmetic = Cosmetic.query.get(cosmetic_id)
    if not cosmetic:
        raise NotFound("COSMETIC_NOT_FOUND|Cosmétique non trouvé.")
    if cosmetic.type == "AVATAR":
        profile_update = UserProfile.query.filter_by(avatar_id=cosmetic_id).all()
        for profile in profile_update:
            profile.avatar_id = random.randint(1, 3)
    elif cosmetic.type == "BANNER":
        profile_update = UserProfile.query.filter_by(banner_id=cosmetic_id).all()
        for profile in profile_update:
            profile.banner_id = random.randint(4, 6)
    db.session.delete(cosmetic)
    db.session.commit()
    return f"Le cosmétique {cosmetic.name} a été supprimé avec succès."

def get_cosmetic_info(cosmetic_id=None):
    if not cosmetic_id:
        cosmetics = Cosmetic.query.all()
        result = []
        for cosmetic in cosmetics:
            result.append({
                "id": cosmetic.id,
                "type": cosmetic.type,
                "name": cosmetic.name,
                "description": cosmetic.description,
                "icon_url": cosmetic.icon.filepath,
                "rarete": cosmetic.rarete,
                "exclu": cosmetic.exclu
            })
        return result
    if not isinstance(cosmetic_id, int):
        raise BadRequest("INVALID_COSMETIC_ID|L'ID du cosmétique doit être un entier.")
    cosmetic = Cosmetic.query.filter_by(id=cosmetic_id).first()
    if not cosmetic:
        raise NotFound("COSMETIC_NOT_FOUND|Cosmetic non trouvé.")
    cosmetic_info = {
        "id": cosmetic.id,
        "type": cosmetic.type,
        "name": cosmetic.name,
        "description": cosmetic.description,
        "icon_url": cosmetic.icon.filepath,
        "rarete": cosmetic.rarete,
    }
    return cosmetic_info

def admin_list_cosmetics():
    cosmetics = Cosmetic.query.all()
    cosmetics_list = []
    for cosmetic in cosmetics:
        cosmetics_list.append({
            "id": cosmetic.id,
            "type": cosmetic.type,
            "name": cosmetic.name,
            "description": cosmetic.description,
            "icon_url": cosmetic.icon.filepath,
            "rarete": cosmetic.rarete,
            "exclu": cosmetic.exclu,
            "created_by": cosmetic.creator.username,
            "created_at": cosmetic.created_at.strftime("%d/%m/%Y %H:%M:%S"),
            "user_count": cosmetic.user_count,
            "active_user_count": cosmetic.active_user,
            "in_active_boutique": cosmetic.in_active_boutique
        })
    return cosmetics_list

def list_cosmetics():
    cosmetics = Cosmetic.query.all()
    cosmetics_list = []
    for cosmetic in cosmetics:
        cosmetics_list.append({
            "id": cosmetic.id,
            "type": cosmetic.type,
            "name": cosmetic.name,
            "description": cosmetic.description,
            "icon_url": cosmetic.icon.filepath,
            "rarete": cosmetic.rarete,
        })
    return cosmetics_list

def assign_cosmetic(target_user_id, cosmetic_id, assign):
    if not isinstance(target_user_id, int):
        raise BadRequest("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    if not isinstance(cosmetic_id, int):
        raise BadRequest("INVALID_COSMETIC_ID|L'ID du cosmétique doit être un entier.")
    if not isinstance(assign, bool):
        raise InternalServerError("INVALID_ASSIGN_VALUE|La valeur d'assignation doit être un booléen.")
    user = User.query.filter_by(id=target_user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    cosmetic = Cosmetic.query.filter_by(id=cosmetic_id).first()
    if not cosmetic:
        raise NotFound("COSMETIC_NOT_FOUND|Cosmétique non trouvé.")
    user_entry = next((entry for entry in user.inventory if entry.cosmetic_id == cosmetic_id), None)
    if assign:
        if user_entry:
            raise Conflict("COSMETIC_ALREADY_OWNED|L'utilisateur possède déjà ce cosmétique.")
        new_entry = UserCosmetic(user_id=target_user_id, cosmetic_id=cosmetic_id)
        db.session.add(new_entry)
    else:
        if not user_entry:
            raise NotFound("COSMETIC_NOT_ASSIGNED|L'utilisateur ne possède pas ce cosmétique.")
        db.session.delete(user_entry)
    db.session.commit()
    return f"Le cosmétique {cosmetic.name} a été {'assigné' if assign else 'retiré'} avec succès à l'utilisateur {user.username}."

def update_cosmetic(user_id, new_cosmetic_id):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    if not isinstance(new_cosmetic_id, int):
        raise BadRequest("INVALID_COSMETIC_ID|L'ID du cosmétique doit être un entier.")
    user = (User.query.filter_by(id=user_id).options(joinedload(User.profile),joinedload(User.inventory).joinedload(UserCosmetic.cosmetic)).first())
    if not user:
        raise InternalServerError("USER_NOT_FOUND|Utilisateur non trouvé.")
    if not user.profile:
        raise InternalServerError("USER_PROFILE_NOT_FOUND|Profil utilisateur non trouvé.")
    cosmetic = Cosmetic.query.filter_by(id=new_cosmetic_id).with_entities(Cosmetic.id).first()
    if not cosmetic:
        raise NotFound("COSMETIC_NOT_FOUND|Cosmétique non trouvé.")
    cosmetic_entry = next((entry for entry in user.inventory if entry.cosmetic_id == new_cosmetic_id), None)
    if not cosmetic_entry:
        raise Forbidden("COSMETIC_NOT_OWNED|L'utilisateur ne possède pas ce cosmétique.")
    cosmetic = cosmetic_entry.cosmetic
    if not AUTHORIZED_COSMETICS_TYPES.get(cosmetic.type):
        raise InternalServerError("INVALID_COSMETIC_TYPE|Type de cosmétique invalide.")
    if cosmetic.type == "AVATAR":
        user.profile.avatar_id = new_cosmetic_id
    elif cosmetic.type == "BANNER":
        user.profile.banner_id = new_cosmetic_id
    db.session.commit()
    return f"Le cosmétique {cosmetic.name} a été mis à jour avec succès pour l'utilisateur."

def get_admin_user_cosmetics(user_id):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = (User.query
            .filter_by(id=user_id)
            .options(joinedload(User.inventory).joinedload(UserCosmetic.cosmetic))
            .first())
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    avatar_cosmetics = []
    banner_cosmetics = []
    for entry in user.inventory:
        cosmetic = entry.cosmetic
        cosmetic_info = {
            "id": cosmetic.id,
            "type": cosmetic.type,
            "name": cosmetic.name,
            "description": cosmetic.description,
            "icon_url": cosmetic.icon.filepath,
            "rarete": cosmetic.rarete,
            "earned_at": entry.earned_at.strftime("%d/%m/%Y %H:%M:%S")
        }
        if cosmetic.type == "AVATAR":
            avatar_cosmetics.append(cosmetic_info)
        elif cosmetic.type == "BANNER":
            banner_cosmetics.append(cosmetic_info)
    return {
        "avatar_list": avatar_cosmetics,
        "banner_list": banner_cosmetics
    }

def get_user_cosmetics(user_id):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = (User.query
            .filter_by(id=user_id)
            .options(joinedload(User.inventory).joinedload(UserCosmetic.cosmetic))
            .first())
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    avatar_cosmetics = []
    banner_cosmetics = []
    for entry in user.inventory:
        cosmetic = entry.cosmetic
        cosmetic_info = {
            "id": cosmetic.id,
            "type": cosmetic.type,
            "name": cosmetic.name,
            "description": cosmetic.description,
            "icon_url": cosmetic.icon.filepath,
            "rarete": cosmetic.rarete,
            "earned_at": entry.earned_at.strftime("%d/%m/%Y %H:%M:%S")
        }
        if cosmetic.type == "AVATAR":
            avatar_cosmetics.append(cosmetic_info)
        elif cosmetic.type == "BANNER":
            banner_cosmetics.append(cosmetic_info)
    return {
        "avatar_list": avatar_cosmetics,
        "banner_list": banner_cosmetics
    }
