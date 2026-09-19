from sqlalchemy import func
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import NotFound, BadRequest, InternalServerError

from extensions import db
from flask import render_template
from datetime import datetime
from extensions import mail_service
from services.session_service import (
    get_connected_users, update_user_session
)
from models.core import (
    User, UserProfile, UserStatusHistory
)
from core.security import (
    reg_verify_username, generate_update_code, verify_update_code,
    reg_verify_passphrase, reg_setup_passphrase, log_verify_passphrase,
    delete_update_code
)

AUTHORIZED_USER_STATUS = {
    "ACTIVE": True,
    "INNACTIVE": True,
    "BANNED": True,
    "LOCKED": True,
    "PENDING": True
}

EMAIL_TEMPLATE_PATHS = {
    "update_passphrase": "mail/update_passphrase.html",
    "update_email": "mail/update_email.html",
    "LOCKED": {"path": "mail/locked_account.html", "subject": "[GuardiaHack] Votre compte a était verrouillé pour raisons de sécurité"},
    "BANNED": {"path": "mail/banned_account.html", "subject": "[GuardiaHack] Votre compte a était suspendu"}
}


def get_user_info(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise InternalServerError("USER_NOT_FOUND|Utilisateur non trouvé.")
    profile = {
        "username": user.username,
        "type": user.type,
        "global_score": user.global_score,
        "xp": user.xp,
        "level": user.level,
        "xp_level": user.next_level_xp[0],
        "next_xp_level":  user.next_level_xp[1],
        "avatar": user.profile.avatar_cosmetic.icon.filepath if user.profile.avatar_cosmetic else None
    }
    return profile

def get_user_profile(target_username):
    user = (User.query.filter_by(username=target_username).first())
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    if user.type == "PEDAGOGIE":
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    profile_info = {
        "username": user.username,
        "type": user.type,
        "global_score": user.global_score,
        "rank": user.rank,
        "xp": user.xp,
        "level": user.level,
        "xp_level": user.next_level_xp[0],
        "next_xp_level":  user.next_level_xp[1],
        "connection_streak": None if user.profile.is_private else user.connection_streak,
        "first_name": None if user.profile.is_private else user.profile.first_name,
        "last_name": None if user.profile.is_private else user.profile.last_name,
        "affiliation": user.profile.affiliation,
        "niveau": user.profile.niveau,
        "classe": user.profile.classe,
        "avatar": user.profile.avatar_cosmetic.icon.filepath if user.profile.avatar_cosmetic else None,
        "banner": user.profile.banner_cosmetic.icon.filepath if user.profile.banner_cosmetic else None,
        "is_private": user.profile.is_private
    }
    return profile_info

def get_own_profile(user_id):
    user = (User.query.filter_by(id=user_id).first())
    if not user:
        raise InternalServerError("USER_NOT_FOUND|Utilisateur non trouvé.")
    profile_info = {
        "username": user.username,
        "type": user.type,
        "global_score": user.global_score,
        "rank": user.rank,
        "xp": user.xp,
        "level": user.level,
        "xp_level": user.next_level_xp[0],
        "next_xp_level":  user.next_level_xp[1],
        "connection_streak": user.connection_streak,
        "first_name": user.profile.first_name,
        "last_name": user.profile.last_name,
        "affiliation": user.profile.affiliation,
        "niveau": user.profile.niveau,
        "classe": user.profile.classe,
        "avatar_id": user.profile.avatar_id,
        "banner_id": user.profile.banner_id,
        "avatar": user.profile.avatar_cosmetic.icon.filepath if user.profile.avatar_cosmetic else None,
        "banner": user.profile.banner_cosmetic.icon.filepath if user.profile.banner_cosmetic else None,
        "is_private": user.profile.is_private
    }
    return profile_info

def get_user_list(offset, affiliation=None, username=None, niveau=None, limit=25):
    if not isinstance(offset, int) or offset < 0:
        offset = 0
    query = User.query.join(User.profile)
    if affiliation:
        query = query.filter(UserProfile.affiliation == affiliation)
    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))
    if niveau:
        query = query.filter(UserProfile.niveau == niveau)
    total_users = query.with_entities(func.count(User.id)).scalar()
    users = query.order_by(User.id.asc()).offset(offset).limit(limit).all()
    user_list = []
    for user in users:
        if user.type == "PEDAGOGIE":
            continue
        profile = user.profile
        user_list.append({
            "username": user.username,
            "avatar": profile.avatar_cosmetic.icon.filepath if profile and profile.avatar_cosmetic else None,
            "affiliation": profile.affiliation if profile else None,
            "niveau": profile.niveau if profile else None,
            "classe": profile.classe if profile else None,
            "level": user.level
        })
    return total_users, user_list

def get_user_list_admin(offset=0, limit=25, search=None, role=None, affiliation=None, status=None, connected=None, sort_by="id", sort_dir="desc"):
    if not isinstance(offset, int) or offset < 0:
        offset = 0
    if not isinstance(limit, int) or limit <= 0:
        limit = 25
    query = User.query.options(joinedload(User.profile))
    if search:
        query = query.filter(User.username.ilike(f"%{search}%"))
    if role:
        query = query.filter(User.type.ilike(role))
    if affiliation:
        query = query.join(UserProfile).filter(UserProfile.affiliation == affiliation)
    if status:
        query = query.filter(User.status == status)
    if connected:
        connected_users_set = get_connected_users()
        if connected_users_set:
            query = query.filter(User.id.in_(connected_users_set))
        else:
            query = query.filter(User.id == -1) # Aucun résultat si personne n'est connecté
    allowed_sorts = {
        "id": User.id,
        "username": User.username,
        "first_name": UserProfile.first_name,
        "last_name": UserProfile.last_name,
        "role": User.type,
        "affiliation": UserProfile.affiliation
    }
    if sort_by in ["first_name", "last_name", "affiliation"]:
        query = query.outerjoin(UserProfile)
    sort_column = allowed_sorts.get(sort_by, User.id)
    if sort_dir == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    total_items = query.with_entities(func.count(User.id)).scalar()
    users = query.offset(offset).limit(limit).all()
    user_list = []
    connected_users_set = get_connected_users() 
    for user in users:
        profile = user.profile 
        user_list.append({
            "id": user.id,
            "username": user.username,
            "first_name": profile.first_name if profile and profile.first_name else "--",
            "last_name": profile.last_name if profile and profile.last_name else "--",
            "mail": user.mail,
            "affiliation": profile.affiliation if profile and profile.affiliation else "--",
            "niveau": profile.niveau if profile and profile.niveau else "--",
            "classe": profile.classe if profile and profile.classe else "--",
            "type": user.type,
            "status": user.status,
            "connected": user.id in connected_users_set
        })
        
    return total_items, user_list


def get_admin_user_info(user_id):
    if not isinstance(user_id, int):
        raise BadRequest("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    user_info = {
        "created_at": user.created_at.strftime("%d/%m/%Y %H:%M:%S"),
        "user_preset": user.user_preset.name if user.user_preset else "Aucun",
        "last_connection": user.last_connection.strftime("%d/%m/%Y %H:%M:%S") if user.last_connection else "Jamais",
        "inventory_count": user.inventory_count,
        "inventory": {
            "badges": [badge.name for badge in user.badges],
            "cosmetics": [item.cosmetic.name for item in user.inventory if item.cosmetic]
        },
        "achievement_count": user.achievements_count,
        "achievements": [a.achievement.name for a in user.achievements if hasattr(a, 'achievement') and a.achievement],
        "status_history": [
            {
                "status": history.status,
                "reason": history.reason,
                "admin_id": history.admin_id,
                "auto": history.auto,
                "created_at": history.changed_at.strftime("%d/%m/%Y %H:%M:%S") if history.changed_at else "—",
                "ended_at": history.ended_at.strftime("%d/%m/%Y %H:%M:%S") if history.ended_at else None
            }
            for history in user.status_history
        ],
        "challenges_count": user.challenges_count,
        "challenges_history": [
            {
                "challenge_name": challenge.challenge.name if challenge.challenge else "Inconnu",
                "submitted_at": challenge.submitted_at.strftime("%d/%m/%Y %H:%M:%S") if challenge.submitted_at else "—",
                "is_correct": challenge.is_correct
            }
            for challenge in user.submissions
        ]
    }
    return user_info


def update_username(user_id, new_username):
    if not isinstance(user_id, int):
        raise BadRequest("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    if not new_username:
        raise BadRequest("NEW_USERNAME_MISSING|Le nouveau nom d'utilisateur est manquant.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    if user.username == new_username:
        raise BadRequest("USERNAME_UNCHANGED|Le nouveau nom d'utilisateur est identique à l'ancien.")
    if User.query.filter_by(username=new_username).first():
        raise BadRequest("USERNAME_TAKEN|Le nom d'utilisateur est déjà pris.")
    reg_verify_username(new_username)
    user.username = new_username
    db.session.commit()
    update_user_session(user_id=user_id, username=new_username)
    return "Nom d'utilisateur mis à jour avec succès."

def update_privacy(user_id, new_privacy_mode):
    if not isinstance(user_id, int):
        raise BadRequest("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    if not isinstance(new_privacy_mode, bool):
        raise BadRequest("NEW_PRIVACY_MODE_INVALID|Valeur de mode de confidentialité invalide. Doit être un booléen.")
    user = User.query.filter_by(id=user_id).options(joinedload(User.profile)).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    if not user.profile:
        raise NotFound("PROFILE_NOT_FOUND|Profil d'utilisateur non trouvé.")
    user.profile.is_private = new_privacy_mode
    db.session.commit()
    privacy_status = "privé" if new_privacy_mode else "public"
    update_user_session(user_id=user_id, is_private=new_privacy_mode)
    return f"Votre profil est désormais {privacy_status}."

def send_update_code(user_id):
    if not isinstance(user_id, int):
        raise BadRequest("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    code = generate_update_code(user_id=user_id)
    email_body = render_template('mail/update_passphrase.html', code=code)
    subject = "[GuardiaHack] Code de mise à jour de mot de passe"
    mail_service.send_email(recipient=user.mail, subject=subject, body=email_body)
    return "Code de sécurité envoyé par mail."

def update_passphrase(user_id, new_passphrase, code):
    if not isinstance(user_id, int):
        raise BadRequest("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    verify_update_code(user_id=user_id, code=code)
    reg_verify_passphrase(passphrase=new_passphrase)
    hashed_passphrase = reg_setup_passphrase(passphrase=new_passphrase)
    if log_verify_passphrase(stored_hash=user.passphrase_hash, provided_passphrase=new_passphrase):
        raise BadRequest("PASSPHRASE_UNCHANGED|La nouvelle passphrase est identique à l'ancienne.")
    user.passphrase_hash = hashed_passphrase
    db.session.commit()
    delete_update_code(user_id)
    return "Passphrase mise à jour avec succès."

def admin_update_user_status(user_id, new_status, reason=None, ended_at=None, admin_id=None, auto=None):
    if not isinstance(user_id, int):
        raise BadRequest("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    if not AUTHORIZED_USER_STATUS.get(new_status):
        raise BadRequest("INVALID_STATUS|Le statut fourni n'est pas valide.")
    is_blocked_status = new_status in ("BANNED", "LOCKED")
    if is_blocked_status and not reason:
        raise BadRequest("REASON_REQUIRED|Une raison est requise pour le bannissement ou le verrouillage.")
    user.status = new_status
    new_status_history = UserStatusHistory()
    new_status_history.user_id = user.id
    new_status_history.status = new_status
    new_status_history.reason = reason
    new_status_history.admin_id = admin_id
    new_status_history.auto = auto
    new_status_history.ended_at = datetime.fromisoformat(ended_at) if ended_at else None
    db.session.add(new_status_history)
    db.session.commit()
    if is_blocked_status:
        info = {
            "first_name": user.profile.first_name,
            "last_name": user.profile.last_name,
            "username": user.username,
            "reason": reason,
            "ended_at": ended_at if ended_at else None
        }
        template_config = EMAIL_TEMPLATE_PATHS.get(new_status)
        if not template_config:
            raise InternalServerError("TEMPLATE_NOT_FOUND|Modèle d'e-mail non trouvé.")
        email_body = render_template(template_config.get("path"), info=info)
        email_subject = template_config.get("subject")
        mail_service.send_email(recipient=user.mail, subject=email_subject, body=email_body)
        if not auto:
            return f"Statut de l'utilisateur mis à jour avec succès. Un e-mail a été envoyé à {user.mail}."
    if not auto:
        return "Statut de l'utilisateur mis à jour avec succès."
