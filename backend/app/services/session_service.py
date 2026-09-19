from flask import current_app, session
from werkzeug.exceptions import InternalServerError, NotFound
from extensions import redis_client

def create_user_session(log_info):
    try:
        session.clear()
        session['user_id'] = log_info.get('user_id')
        session['username'] = log_info.get('username')
        session['type'] = log_info.get('type')
        session['is_private'] = log_info.get('is_private')
    except Exception as e:
        raise InternalServerError("SESSION_CREATION_FAILED|Erreur lors de la création de la session.")

def clear_user_session():
    try:
        session.clear()
        user_id = session.get('user_id')
        if user_id:
            redis_client.delete(f"online_user:{user_id}")
    except Exception as e:
        current_app.logger.warning(f"Erreur lors de la suppression de la session: {str(e)}")
        raise InternalServerError("LOGOUT_FAILED|Erreur lors de la déconnexion.")

def get_user_session():
    if 'user_id' not in session:
        raise NotFound("SESSION_NOT_FOUND|Aucune session utilisateur trouvée.")
    return {
        'user_id': session['user_id'],
        'username': session['username'],
        'type': session['type'],
        'is_private': session.get('is_private')
    }

def update_user_session(user_id, username=None, user_type=None, is_private=None):
    try:
        session['user_id'] = user_id
        session['username'] = username if username is not None else session.get('username')
        session['type'] = user_type if user_type is not None else session.get('type')
        session['is_private'] = is_private if is_private is not None else session.get('is_private')
    except Exception as e:
        raise InternalServerError("SESSION_UPDATE_FAILED|Erreur lors de la mise à jour de la session.")

def get_connected_users():
    keys = redis_client.keys("online_user:*")
    return {int((k.decode('utf-8') if isinstance(k, bytes) else k).split(':')[1]) for k in keys if k}
