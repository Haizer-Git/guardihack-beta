from numpy import random
from werkzeug.exceptions import BadRequest, Conflict, InternalServerError, NotFound, Unauthorized

from extensions import db
from datetime import datetime, timezone
from extensions import mail_service, redis_client
from services.notification_service import(
    send_notification
)
from flask import current_app, render_template
from models.core import (
    User, PresetToken, UserProfile, UserPreset
)
from core.security import (
    reg_verify_username, reg_verify_passphrase, reg_setup_passphrase,
    log_verify_passphrase, generate_token, generate_reset_url,
    verify_reset_token
)
from services.xp_service import (
    daily_xp_bonus
)

TOKEN_STATUS = {
    "EXPIRED": "Le token a expiré.",
    "MAX_USES_REACHED": "Le token a atteint le nombre maximum d'utilisations.",
    "ACTIVE": "Le token est actif."
}


def create_token(user_id, data, auto=None):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = User.query.filter_by(id=user_id).with_entities(User.id).first()
    # if not user:
    #     raise NotFound("USER_NOT_FOUND|L'utilisateur créant le token n'existe pas.")
    if not isinstance(data, dict):
        raise BadRequest("INVALID_DATA|Les données doivent être un dictionnaire.")
    if not data.get('preset_id'):
        raise BadRequest("MISSING_PRESET_ID|Un preset est requis pour générer un token.")
    preset_id = data['preset_id']
    if not isinstance(preset_id, int):
        raise BadRequest("INVALID_PRESET_ID|L'ID du preset doit être un entier.")
    preset = UserPreset.query.filter_by(id=preset_id).with_entities(UserPreset.id).first()
    if not preset:
        raise NotFound("PRESET_NOT_FOUND|Le preset spécifié n'existe pas.")
    if data.get('expires_at') :
        expires_at = data['expires_at']
        if not isinstance(expires_at, datetime):
            if expires_at.endswith('Z'):
                expires_at = expires_at.replace('Z', '+00:00')
            expires_at_obj = datetime.fromisoformat(expires_at)
        if expires_at_obj < datetime.now(timezone.utc):
            raise BadRequest("INVALID_EXPIRATION_DATE|La date d'expiration doit être dans le futur.")
    if data.get('max_uses') is not None and (not isinstance(data['max_uses'], int) or data['max_uses'] <= 0):
        raise BadRequest("INVALID_MAX_USES|Le nombre maximum d'utilisations doit être un entier positif.")
    if data.get('mail'):
        if '@' not in data['mail']:
            raise BadRequest("INVALID_MAIL|L'adresse e-mail fournie est invalide.")
        existing_mail = User.query.filter_by(mail=data['mail']).with_entities(User.mail).first()
        if existing_mail:
            raise Conflict("MAIL_ALREADY_EXISTS|L'adresse e-mail fournie est déjà utilisée.")
    new_token = PresetToken()
    new_token.preset_id = preset_id
    new_token.token = generate_token()
    new_token.max_uses = data.get('max_uses')
    new_token.expires_at = expires_at_obj if data.get('expires_at') else None
    new_token.created_by = user_id
    new_token.created_at = datetime.now()
    new_token.mail = data.get('mail')
    new_token.first_name = data.get('first_name')
    new_token.last_name = data.get('last_name')
    new_token.classe = data.get('classe')
    new_token.niveau = data.get('niveau')
    new_token.auto = auto if auto is not None else False
    db.session.add(new_token)
    db.session.commit()
    if auto:
        return new_token.id, new_token.token
    return "Token créé avec succès"

def delete_token(token_id):
    if not isinstance(token_id, int):
        raise BadRequest("INVALID_TOKEN_ID|L'ID du token doit être un entier.")
    preset_token = PresetToken.query.filter_by(id=token_id).first()
    if not preset_token:
        raise NotFound("TOKEN_NOT_FOUND|Le token spécifié n'existe pas.")
    db.session.delete(preset_token)
    db.session.commit()
    return "Token supprimé avec succès."

def validate_token(token):
    token = PresetToken.query.filter_by(token=token).first()
    if not token:
        raise NotFound("TOKEN_INVALID|Le token spécifié n'existe pas ou n'est lié à aucun preset.")
    if token.is_active != "ACTIVE":
        raise BadRequest(f"TOKEN_INVALID|{TOKEN_STATUS[token.is_active]}")
    user_preset = UserPreset.query.filter_by(id=token.preset_id).first()
    if not user_preset:
        raise NotFound("PRESET_NOT_FOUND|Le preset associé au token n'existe pas.")
    preset_info = {
        "mail": token.mail if token.mail else None,
        "type": token.preset.type,
        "first_name": token.first_name if token.first_name else None,
        "last_name": token.last_name if token.last_name else None,
        "affiliation": token.preset.affiliation,
        "niveau": token.niveau if token.niveau else None,
        "classe": token.classe if token.classe else None
    }
    return preset_info

def list_tokens():
    tokens = PresetToken.query.all()
    result = []
    for t in tokens:
        result.append({
            "id": t.id,
            "preset_id": t.preset_id,
            "token": t.token,
            "uses": t.uses,
            "max_uses": t.max_uses,
            "expires_at": t.expires_at.strftime("%d/%m/%Y %H:%M:%S") if t.expires_at else None,
            "created_by": t.creator.username if t.creator else None,
            "created_at": t.created_at.strftime("%d/%m/%Y %H:%M:%S"),
            "mail": t.mail,
            "first_name": t.first_name,
            "last_name": t.last_name,
            "classe": t.classe,
            "niveau": t.niveau,
            "is_active": t.is_active,
            "auto": t.auto
        })
    return result

def get_token_by_id(token_id):
    if not isinstance(token_id, int):
        raise BadRequest("INVALID_TOKEN_ID|L'ID du token doit être un entier.")
    token = PresetToken.query.filter_by(id=token_id).first()
    if not token:
        raise NotFound("TOKEN_NOT_FOUND|Le token spécifié n'existe pas.")
    token_info = {
        "id": token.id,
        "preset_id": token.preset_id,
        "token": token.token,
        "uses": token.uses,
        "max_uses": token.max_uses,
        "expires_at": token.expires_at.strftime("%d/%m/%Y %H:%M:%S") if token.expires_at else None,
        "created_by": token.creator.username if token.creator else None,
        "created_at": token.created_at.strftime("%d/%m/%Y %H:%M:%S"),
        "mail": token.mail,
        "first_name": token.first_name,
        "last_name": token.last_name,
        "is_active": token.is_active
    }
    return token_info

def send_token(token_id):
    if not isinstance(token_id, int):
        raise BadRequest("INVALID_TOKEN_ID|L'ID du token doit être un entier.")
    preset_token = PresetToken.query.filter_by(id=token_id).first()
    if not preset_token:
        raise NotFound("TOKEN_NOT_FOUND|Le token spécifié n'existe pas.")
    if not preset_token.mail:
        raise BadRequest("MAIL_MISSING|Le token n'a pas d'adresse e-mail associée.")
    subject = "Bienvenue chez GuardiHack"
    email_body = render_template('mail/token_notification.html', token=preset_token)
    try:
        mail_service.send_email(recipient=preset_token.mail, subject=subject, body=email_body)
        return "E-mail de notification envoyé avec succès."
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'envoi de l'email de notification: {str(e)}")
        raise InternalServerError("EMAIL_FAILED|Erreur lors de l'envoi de l'email de notification.")

def register_user(data):
    required_fields = ['username', 'passphrase', 'mail', 'first_name', 'last_name', 'token']
    for field in required_fields:
        if not data.get(field):
            raise BadRequest(f"{field.upper()}_MISSING|Il manque le champs {field}")
    token_str = data['token']
    username = data['username']
    passphrase = data['passphrase']
    form_mail = data['mail']
    form_first_name = data['first_name']
    form_last_name = data['last_name']
    preset_token = PresetToken.query.filter_by(token=token_str).first()
    if not preset_token:
        raise NotFound("TOKEN_INVALID|Le token fourni n'existe pas ou n'est lié à aucun preset.")
    if preset_token.max_uses is not None and preset_token.uses >= preset_token.max_uses:
        raise BadRequest("TOKEN_MAX_USES|Le token a atteint le nombre maximum d'utilisations.")
    if preset_token.expires_at is not None:
        now_str = datetime.now()
        date = str(preset_token.expires_at)
        if date < now_str:
            raise BadRequest("TOKEN_EXPIRED|Le token a expiré.")
    if User.query.filter_by(username=username).first():
        raise Conflict("USERNAME_TAKEN|Nom d'utilisateur déjà pris")
    final_mail = preset_token.mail if preset_token.mail else form_mail
    if User.query.filter_by(mail=final_mail).first():
        raise Conflict("MAIL_TAKEN|Adresse email déjà utilisée")
    reg_verify_username(username)
    reg_verify_passphrase(passphrase)
    hashed_passphrase = reg_setup_passphrase(passphrase)
    user_preset = preset_token.preset
    if not user_preset:
        raise NotFound("PRESET_NOT_FOUND|Le preset associé au token n'existe pas.")
    new_user = User()
    new_user.username = username
    new_user.mail = final_mail
    new_user.passphrase_hash = hashed_passphrase
    new_user.type = user_preset.type
    new_user.preset_id = user_preset.id
    new_user.secret_key = generate_token()
    new_user.status = "ACTIVE" if user_preset.type == "ADMIN" else "PENDING"
    db.session.add(new_user)
    preset_token.uses += 1
    db.session.commit()
    new_user_profiles = UserProfile()
    new_user_profiles.user_id = new_user.id
    new_user_profiles.first_name = preset_token.first_name if preset_token.first_name else form_first_name
    new_user_profiles.last_name = preset_token.last_name if preset_token.last_name else form_last_name
    new_user_profiles.affiliation = user_preset.affiliation
    new_user_profiles.niveau = preset_token.niveau if preset_token.niveau else None
    new_user_profiles.classe = preset_token.classe if preset_token.classe else None
    new_user_profiles.is_private = True
    db.session.add(new_user_profiles)
    db.session.commit()
    log_info = {
        "user_id": new_user.id,
        "username": new_user.username,
        "type": new_user.type,
        "is_private": new_user_profiles.is_private
    }
    return log_info, "Inscription réussie. Bienvenue sur GuardiHack !"

def login_user(data):
    required_fields = ['mail', 'passphrase']
    for field in required_fields:
        if not data.get(field):
            raise BadRequest("CREDENTIALS_MISSING|E-mail ou mot de passe manquant.")
    mail = data['mail']
    passphrase = data['passphrase']
    user = User.query.filter_by(mail=mail).first()
    bonus = None
    if not user:
        raise NotFound("WRONG_CREDENTIALS|E-mail ou mot de passe incorrect.")
    if user.status == "BANNED":
        raise Unauthorized("USER_BANNED|Votre compte fait actuellement l'objet un banissement. Veuillez contacter un administrateur pour plus d'informations.")
    if user.status == "INNACTIVE":
        raise Unauthorized("USER_INACTIVE|Votre compte est actuellement désactivé. Veuillez contacter un administrateur pour l'activer.")
    if user.status == "LOCKED":
        raise Unauthorized("USER_LOCKED|Votre compte est actuellement verrouillé pour des raisons de sécurité. Veuillez contacter un administrateur pour le déverrouiller.")
    if not log_verify_passphrase(stored_hash=user.passphrase_hash, provided_passphrase=passphrase):
        raise BadRequest("WRONG_CREDENTIALS|E-mail ou mot de passe incorrect.")
    try:
        if user.last_connection:
            time_since_last = datetime.now() - user.last_connection
            if time_since_last.total_seconds() > 24 * 3600:
                user.connection_streak += 1
                bonus = daily_xp_bonus(user_id=user.id, streak=user.connection_streak)
            else:
                user.connection_streak = 0
        user.last_connection = datetime.now()
        db.session.commit()
    except Exception as e:
        current_app.logger.warning(f"Erreur lors de la gestion des achievements de connexion: {str(e)}")
    user_info = {
        "user_id": user.id,
        "username": user.username,
        "type": user.type,
        "status": user.status,
        "is_private": user.profile.is_private
    }
    if bonus:
        return user_info, f"Connexion réussie. Vous avez gagné {int(bonus)} XP pour votre connexion quotidienne depuis {user.connection_streak} jours !"
    send_notification(user_id=user.id, title="Connexion réussie", message="Vous vous êtes connecté avec succès à GuardiHack.")
    return user_info, "Connexion réussie."

def send_reset_code(mail):
    if not mail:
        raise BadRequest("MAIL_MISSING|E-mail manquant.")
    message = "Si un compte associé à ce mail existe, un lien a été envoyé."
    user = User.query.filter_by(mail=mail).with_entities(User.mail, User.id).first()
    if not user:
        return message
    url = generate_reset_url(user.id)
    email_body = render_template('mail/reset_passphrase.html', reset_url=url)
    subject = "Réinitialisation de votre mot de passe"
    try:
        mail_service.send_email(recipient=mail, subject=subject, body=email_body)
        return message
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'envoi de l'email de réinitialisation: {str(e)}")
        raise InternalServerError("EMAIL_FAILED|Erreur lors de l'envoi de l'email de réinitialisation.")

def reset_passphrase(data):
    if not data.get('token'):
        raise BadRequest("TOKEN_MISSING|Le token de réinitialisation est manquant.")
    if not data.get('new_passphrase'):
        raise BadRequest("NEW_PASSPHRASE_MISSING|La nouvelle passphrase est manquante.")
    token = data['token']
    new_passphrase = data['new_passphrase']
    user_id = verify_reset_token(token=token)[1]
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    if log_verify_passphrase(stored_hash=user.passphrase_hash, provided_passphrase=new_passphrase):
        raise BadRequest("PASSPHRASE_SAME|La nouvelle passphrase ne peut pas être la même que l'ancienne.")
    reg_verify_passphrase(new_passphrase)
    user.passphrase_hash = reg_setup_passphrase(new_passphrase)
    db.session.commit()
    redis_client.delete(f"reset_token:{token}")
    return "Passphrase réinitialisée avec succès."