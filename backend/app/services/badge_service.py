from sqlalchemy.orm import joinedload
from werkzeug.exceptions import Conflict, InternalServerError, NotFound, BadRequest

from extensions import db
from models.core import (
    Badge, UserBadge, User,
    Icon
)
AUTHORIZED_REQUIREMENTS = {
    "CHALLENGE_ID": True,
    "SOLVE_COUNT": True,
    "SCORE": True,
    "CATEGORY_SOLVE_COUNT": True,
    "CONNECTION_STREAK": True,
    "CONNECTION_DATE": True
}

AUTHORIZED_BADGE_TYPES = {
    "CHALLENGE": True,
    "ACHIEVEMENT": True,
    "SPECIAL": True,
    "ADMIN": True
}

def get_user_badge(target_username):
    user = User.query.filter_by(username=target_username).options(joinedload(User.badges)).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    list_badges = []
    for badge in user.badges:
        list_badges.append({
            "id": badge.id,
            "type": badge.type,
            "name": badge.name,
            "description": badge.description,
            "icon_url": badge.icon.filepath,
        })
    return list_badges

def create_badge(user_id, badge_info):
    required_fields = ['name', 'description', 'type', 'icon_id']
    for field in required_fields:
        if field not in badge_info or badge_info.get(field) is None:
            raise BadRequest(f"MISSING_FIELD|Le champ '{field}' est requis pour créer un badge.")
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = User.query.filter_by(id=user_id).with_entities(User.id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|L'utilisateur créant le badge n'existe pas.")
    if not isinstance(badge_info, dict):
        raise BadRequest("INVALID_BADGE_DATA|Les informations du badge doivent être sous forme de dictionnaire.")
    name = badge_info['name']
    description = badge_info['description']
    badge_type = badge_info['type']
    icon_id = badge_info["icon_id"]
    if not isinstance(icon_id, int):
        raise BadRequest("INVALID_ICON_ID|L'ID de l'icône doit être un entier.")
    icons = Icon.query.filter_by(id=icon_id).with_entities(Icon.id).first()
    if not icons:
        raise BadRequest("INVALID_ICON_ID|L'icône spécifiée n'existe pas.")
    if not AUTHORIZED_BADGE_TYPES.get(badge_type):
        raise BadRequest("INVALID_BADGE_TYPE|Type de badge invalide.")
    badges = Badge.query.filter_by(name=name).with_entities(Badge.id).first() is not None
    if badges:
        raise Conflict("BADGE_ALREADY_EXISTS|Un badge avec ce nom existe déjà.")
    new_badge = Badge(
        type=badge_type,
        name=name,
        description=description,
        icon_id=icon_id,
        created_by=user_id
    )
    db.session.add(new_badge)
    db.session.commit()
    return f"Le badge {name} a été créé avec succès."

def modify_badge(badge_id, badge_info):
    if not isinstance(badge_id, int):
        raise BadRequest("INVALID_BADGE_ID|L'ID du badge doit être un entier.")
    if not isinstance(badge_info, dict):
        raise BadRequest("INVALID_BADGE_DATA|Les informations du badge doivent être sous forme de dictionnaire.")
    badge = Badge.query.filter_by(id=badge_id).first()
    if not badge:
        raise NotFound("BADGE_NOT_FOUND|Badge non trouvé.")
    modification = False
    if 'new_name' in badge_info:
        new_name = badge_info['new_name']
        name_exists = Badge.query.filter(Badge.name == new_name, Badge.id != badge_id).with_entities(Badge.id).first()
        if name_exists:
            raise Conflict("BADGE_ALREADY_EXISTS|Un badge avec ce nom existe déjà.")
        badge.name = new_name
        modification = True
    if 'new_description' in badge_info:
        badge.description = badge_info['new_description']
        modification = True
    if 'new_type' in badge_info:
        new_type = badge_info['new_type']
        if not AUTHORIZED_BADGE_TYPES.get(new_type):
            raise BadRequest("INVALID_BADGE_TYPE|Type de badge invalide.")
        badge.type = new_type
        modification = True
    if 'new_icon_id' in badge_info:
        new_icon_id = badge_info['new_icon_id']
        if not isinstance(new_icon_id, int):
            raise BadRequest("INVALID_ICON_ID|L'ID de l'icône doit être un entier.")
        icon = Icon.query.filter_by(id=new_icon_id).with_entities(Icon.id).first()
        if not icon:
            raise NotFound("ICON_NOT_FOUND|L'icône spécifiée n'existe pas.")
        badge.icon_id = new_icon_id
        modification = True
    if modification:
        db.session.commit()
        return f"Le badge {badge.name} a été modifié avec succès."
    else : 
        raise BadRequest("NO_MODIFICATIONS|Aucune modification n'a été apportée au badge.")

def list_badges(user_id):
    user_exists = User.query.filter_by(id=user_id).with_entities(User.id).first()
    if not user_exists:
        raise NotFound("USER_NOT_FOUND|L'utilisateur spécifié n'existe pas.")
    badges = Badge.query.all()
    user_badges_data = (UserBadge.query.filter_by(user_id=user_id).with_entities(UserBadge.badge_id, UserBadge.earned_at).all())
    user_badge_map = {ub.badge_id: ub.earned_at for ub in user_badges_data}
    badges_list = []
    for badge in badges:
        earned_at = user_badge_map.get(badge.id)
        badges_list.append({
            "id": badge.id,
            "type": badge.type,
            "name": badge.name,
            "description": badge.description,
            "icon_url": badge.icon.filepath,
            "is_earned": earned_at.strftime("%d/%m/%Y %H:%M:%S") if earned_at else None
        })
    return badges_list

def admin_list_badges():
    badges = Badge.query.all()
    badges_list = []
    for badge in badges:
        badges_list.append({
            "id": badge.id,
            "type": badge.type,
            "name": badge.name,
            "description": badge.description,
            "icon_url": badge.icon.filepath,
            "created_by": badge.creator.username,
            "user_count": badge.user_count
        })
    return badges_list

def get_badge_stats(badge_id):
    if not isinstance(badge_id, int):
        raise BadRequest("INVALID_BADGE_ID|L'ID du badge doit être un entier.")
    result = []
    users = User.query.join(UserBadge).filter(UserBadge.badge_id == badge_id).all()
    for user in users:
        earned_at = next((ub.earned_at for ub in user.badges if ub.id == badge_id), None)
        result.append({
            "user_id": user.id,
            "username": user.username,
            "earned_at": earned_at.strftime("%d/%m/%Y %H:%M:%S") if earned_at else None
        })
    return result

def delete_badge(badge_id):
    if not isinstance(badge_id, int):
        raise BadRequest("INVALID_BADGE_ID|L'ID du badge doit être un entier.")
    badge = Badge.query.filter_by(id=badge_id).first()
    if not badge:
        raise NotFound("BADGE_NOT_FOUND|Le badge spécifié n'existe pas.")
    UserBadge.query.filter_by(badge_id=badge_id).delete()
    db.session.delete(badge)
    db.session.commit()
    return "Badge supprimé avec succès."

def assign_badge(target_user_id, badge_id, assign):
    if not isinstance(target_user_id, int):
        raise BadRequest("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    if not isinstance(badge_id, int):
        raise BadRequest("INVALID_BADGE_ID|L'ID du badge doit être un entier.")
    if not isinstance(assign, bool):
        raise InternalServerError("INVALID_ASSIGN_VALUE|La valeur d'assignation doit être un booléen.")
    user = User.query.filter_by(id=target_user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|L'utilisateur spécifié n'existe pas.")
    badge = Badge.query.filter_by(id=badge_id).first()
    if not badge:
        raise NotFound("BADGE_NOT_FOUND|Le badge spécifié n'existe pas.")
    if assign:
        if badge in user.badges:
            raise Conflict("BADGE_ALREADY_OWNED|L'utilisateur possède déjà ce badge.")
        user.badges.append(badge)
    else:
        if badge not in user.badges:
            raise Conflict("BADGE_NOT_OWNED|L'utilisateur ne possède pas ce badge.")
        user.badges.remove(badge)
    db.session.commit()
    return f"Le badge {badge.name} a été {'attribué' if assign else 'retiré'} à l'utilisateur {user.username} avec succès."