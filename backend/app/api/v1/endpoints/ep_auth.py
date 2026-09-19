from flask import (
    Blueprint, request, jsonify
)
from services.auth_service import (
    register_user, login_user, validate_token,
    send_reset_code, reset_passphrase
)
from services.session_service import (
    create_user_session, clear_user_session, get_user_session
)
from .middleware.mid_auth import (
    login_required
)
from core.security import (
    verify_reset_token
)
from flasgger import swag_from

auth = Blueprint('auth', __name__)


@auth.route('/api/auth/token/<string:token>', methods=['GET'])
@swag_from('../docs/auth/verify_token.yaml')
def api_validate_token(token):
    return jsonify({
        "status": "success",
        "preset": validate_token(token=token)
    }), 200

@auth.route('/api/auth/register', methods=['POST'])
@swag_from('../docs/auth/register.yaml')
def api_register():
    data = request.get_json()
    reg_info, reg_message = register_user(data=data)
    create_user_session(log_info=reg_info)
    return jsonify({
        "status": "success",
        "message": reg_message,
        "user": reg_info
    }), 201
    

@auth.route('/api/auth/login', methods=['POST'])
@swag_from('../docs/auth/login.yaml')
def api_login():
    data = request.get_json()
    log_info, log_message = login_user(data)
    create_user_session(log_info=log_info)
    return jsonify({
        "status": "success",
        "message": log_message,
        "user": log_info
    }), 200

@auth.route('/api/auth/logout', methods=['POST'])
@login_required
@swag_from('../docs/auth/logout.yaml')
def api_logout():
    clear_user_session()
    return jsonify({
        "status": "success",
        "message": "Déconnexion réussie"
    }), 200

@auth.route('/api/auth/session', methods=['GET'])
@login_required
@swag_from('../docs/auth/session.yaml')
def api_session():
    return jsonify({
        "status": "success",
        "session": get_user_session()
    }), 200


@auth.route('/api/auth/passphrase/reset/url', methods=['POST'])
@swag_from('../docs/auth/passphrase_reset_url.yaml')
def api_passphrase_reset():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": send_reset_code(mail=data.get('mail'))
    }), 200

@auth.route('/api/auth/passphrase/reset/<string:token>', methods=['GET'])
@swag_from('../docs/auth/passphrase_reset_verify.yaml')
def api_passphrase_reset_verify(token):
    return jsonify({
        "status": "success",
        "message": verify_reset_token(token=token)[0]
    }), 200

@auth.route('/api/auth/passphrase/reset', methods=['POST'])
@swag_from('../docs/auth/passphrase_reset_confirm.yaml')
def api_passphrase_reset_confirm():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": reset_passphrase(data=data)
    }), 200

