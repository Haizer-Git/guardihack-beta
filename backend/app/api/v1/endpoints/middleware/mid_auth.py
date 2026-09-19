from functools import wraps
from flask import session, jsonify # pyright: ignore[reportMissingImports]


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                "status": "error",
                "slug": "UNAUTHORIZED",
                "message": "Vous devez être connecté pour accéder à cette ressource"
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('type') != 'ADMIN':
            return jsonify({
                "status": "error",
                "slug": "FORBIDDEN",
                "message": "Vous n'avez pas les permissions nécessaires pour accéder à cette ressource"
            }), 403
        return f(*args, **kwargs)
    return decorated_function