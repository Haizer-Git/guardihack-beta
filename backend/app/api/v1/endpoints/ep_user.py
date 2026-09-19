from flask import (
    Blueprint, request, jsonify
)

from services.boutique_service import (
    get_active_boutique
)
from services.session_service import (
    get_user_session
)
from .middleware.mid_auth import (
    login_required
)
from services.user_service import (
    get_own_profile, get_user_profile, update_username,
    update_privacy, send_update_code, verify_update_code, 
    update_passphrase, get_user_list, get_user_info
)
from services.badge_service import (
    get_user_badge, list_badges
)
from services.score_service import (
    get_score_history, get_recent_activity,
    get_leaderboard
)
from services.challenge_service import (
    list_challenge_files, validate_challenge, get_challenge, get_challenge_info, 
    get_user_challenge, get_statistics, list_challenge_category
)

from services.notification_service import (
    get_all_notifications, get_new_notifications, count_notification,
    read_notification, unread_notification, read_global_notification, 
    unread_global_notification
)
from services.cosmetic_service import (
    get_user_cosmetics, update_cosmetic
)
from services.instance_service import (
    launch_instance_for_user,
    stop_instance_for_user
)

from flasgger import swag_from
user = Blueprint('user', __name__)

## ---- PROFILE ENDPOINTS ---- ##

@user.route('/api/user/me', methods=['GET'])
@login_required
@swag_from('../docs/user/info/me.yaml')
def api_get_current_user():
    return jsonify({
        "status": "success",
        "profile": get_user_info(user_id=get_user_session().get('user_id'))
    }), 200

@user.route('/api/user/me/profile', methods=['GET'])
@login_required
@swag_from('../docs/user/info/profile_me.yaml')
def api_get_current_profile():
    return jsonify({
        "status": "success",
        "profile": get_own_profile(user_id=get_user_session().get('user_id'))
    }), 200

@user.route('/api/user/<string:target_username>/profile', methods=['GET'])
@login_required
@swag_from('../docs/user/info/profile_user.yaml')
def api_get_user_profile(target_username):
    return jsonify({
        "status": "success",
        "profile": get_user_profile(target_username=target_username)
    }), 200

@user.route('/api/user/<string:target_username>/badge', methods=['GET'])
@login_required
@swag_from('../docs/user/badge/badges_user.yaml')
def api_get_user_badges_user(target_username):
    return jsonify({
        "status": "success",
        "badges": get_user_badge(target_username=target_username)
    }), 200

@user.route('/api/user/<string:target_username>/score/history', methods=['GET'])
@login_required
@swag_from('../docs/user/score/score_history_user.yaml')
def api_get_score_history_user(target_username):
    return jsonify({
        "status": "success",
        "history": get_score_history(target_username=target_username)
    }), 200

@user.route('/api/user/<string:target_username>/score/recent', methods=['GET'])
@login_required
@swag_from('../docs/user/score/recent_score_user.yaml')
def api_get_recent_score_user(target_username):
    return jsonify({
        "status": "success",
        "history": get_recent_activity(target_username=target_username)
    }), 200

@user.route('/api/user/<string:target_username>/challenge', methods=['GET'])
@login_required
@swag_from('../docs/user/info/challenge_user.yaml')
def api_get_user_challenges_user(target_username):
    return jsonify({
        "status": "success",
        "challenges": get_user_challenge(target_username=target_username)
    }), 200

@user.route('/api/user/<string:target_username>/challenge/statistics', methods=['GET'])
@login_required
#@swag_from('../docs/user/info/statistics_user.yaml')
def api_get_statistics_user(target_username):
    return jsonify({
        "status": "success",
        "statistics": get_statistics(target_username=target_username)
    }), 200


## -- -- UPDATE ENDPOINTS ---- ##

@user.route('/api/user/update/username', methods=['POST'])
@login_required
#@swag_from('../docs/user/update/update_username.yaml')
def api_update_username():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": update_username(user_id=get_user_session().get('user_id'), new_username=data.get('new_username'))
    }), 200

@user.route('/api/user/update/privacy', methods=['POST'])
@login_required
#@swag_from('../docs/user/update/update_privacy.yaml')
def api_update_privacy():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": update_privacy(user_id=get_user_session().get('user_id'), new_privacy_mode=data.get('new_privacy_mode'))
    }), 200

@user.route('/api/user/update/cosmetic', methods=['POST'])
@login_required
@swag_from('../docs/user/update/update_cosmetic.yaml')
def api_update_cosmetic():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": update_cosmetic(user_id=get_user_session().get('user_id'), new_cosmetic_id=data.get('new_cosmetic_id'))
    }), 200

@user.route('/api/user/cosmetic/list', methods=['GET'])
@login_required
@swag_from('../docs/user/cosmetic/cosmetic_list.yaml')
def api_list_cosmetics():
    return jsonify({
        "status": "success",
        "cosmetics": get_user_cosmetics(user_id=get_user_session().get('user_id'))
    }), 200

@user.route('/api/user/update/passphrase/code', methods=['GET'])
@login_required
#@swag_from('../docs/user/update/update_passphrase_code.yaml')
def api_update_passphrase():
    return jsonify({
        "status": "success",
        "message": send_update_code(user_id=get_user_session().get('user_id'))
    }), 200

@user.route('/api/user/update/passphrase/verify', methods=['POST'])
@login_required
#@swag_from('../docs/user/update/update_passphrase_verify.yaml')
def api_update_passphrase_verify():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": verify_update_code(user_id=get_user_session().get('user_id'), code=data.get('code'))
    }), 200

@user.route('/api/user/update/passphrase', methods=['POST'])
@login_required
#@swag_from('../docs/user/update/update_passphrase_confirm.yaml')
def api_update_passphrase_confirm():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": update_passphrase(user_id=get_user_session().get('user_id'), new_passphrase=data.get('new_passphrase'), code=data.get('code'))
    }), 200

## ---- LISTING ENDPOINTS ---- ##

@user.route('/api/user/score/leaderboard/<int:offset>', methods=['GET'])
@login_required
#@swag_from('../docs/user/score/leaderboard.yaml')
def api_get_leaderboard(offset):
    total_users, leaderboard = get_leaderboard(offset=offset)
    return jsonify({
        "status": "success",
        "total_users": total_users,
        "leaderboard": leaderboard
    }), 200

@user.route('/api/user/list/<int:offset>', methods=['GET'])
@login_required
@swag_from('../docs/user/info/list.yaml')
def api_get_user_list(offset):
    total_users, user_list = get_user_list(offset=offset)
    return jsonify({
        "status": "success",
        "total_users": total_users,
        "users": user_list
    }), 200

@user.route('/api/user/list/search', methods=['GET'])
@login_required
# @swag_from('../docs/user/info/list_search.yaml')
def api_search_user_list():
    offset = request.args.get('offset', default=0, type=int)
    affiliation = request.args.get('affiliation', default=None, type=str)
    username = request.args.get('username', default=None, type=str)
    niveau = request.args.get('niveau', default=None, type=str)
    total_users, user_list = get_user_list(
        offset=offset, 
        affiliation=affiliation, 
        username=username, 
        niveau=niveau
    )
    return jsonify({
        "status": "success",
        "total_users": total_users,
        "users": user_list
    }), 200

@user.route('/api/user/badge/list', methods=['GET'])
@login_required
@swag_from('../docs/user/badge/list.yaml')
def api_list_badges():
    return jsonify({
        "status": "success",
        "badges": list_badges(user_id=get_user_session().get('user_id'))
    }), 200


@user.route('/api/user/challenge/list', methods=['GET'])
@login_required
@swag_from('../docs/user/challenge/list.yaml')
def api_list_challenges():
    return jsonify({
        "status": "success",
        "challenges": get_challenge(user_id=get_user_session().get('user_id'), type="ACTIVE")
    }), 200

@user.route('/api/user/challenge/category/list', methods=['GET'])
@login_required
#@swag_from('../docs/user/challenge/category_list.yaml')
def api_list_challenge_categories():
    return jsonify({
        "status": "success",
        "categories": list_challenge_category()
    }), 200

@user.route('/api/user/challenge/search/<string:type>/<string:filter>', methods=['GET'])
@login_required
#@swag_from('../docs/user/challenge/search.yaml')
def api_search_challenge(type, filter):
    return jsonify({
        "status": "success",
        "challenges": get_challenge(user_id=get_user_session().get('user_id'), type=type, filter=filter)
    }), 200

@user.route('/api/user/challenge/<int:challenge_id>/info', methods=['GET'])
@login_required
@swag_from('../docs/user/challenge/info.yaml')
def api_challenge_info(challenge_id):
    return jsonify({
        "status": "success",
        "challenge": get_challenge_info(user_id=get_user_session().get('user_id'), challenge_id=challenge_id)
    }), 200

@user.route('/api/user/challenge/<int:challenge_id>/validate', methods=['POST'])
@login_required
@swag_from('../docs/user/challenge/validate.yaml')
def api_validate_challenge(challenge_id):
    data = request.get_json()
    completion_info, message = validate_challenge(user_id=get_user_session().get('user_id'), challenge_id=challenge_id, flag=data.get('flag'))
    return jsonify({
        "status": "success",
        "message": message,
        "points_awarded": completion_info.get("points_awarded"),
        "xp_awarded": completion_info.get("xp_awarded"),
    }), 200

@user.route('/api/user/notification/new', methods=['GET'])
@login_required
#@swag_from('../docs/user/notification/new.yaml')
def api_get_new_notifications():
    notifications, count = get_new_notifications(user_id=get_user_session().get('user_id'))
    return jsonify({
        "status": "success",
        "notifications": notifications,
        "unread_count": count
    }), 200

@user.route('/api/user/notification/all', methods=['GET'])
@login_required
#@swag_from('../docs/user/notification/all.yaml')
def api_get_all_notifications():
    return jsonify({
        "status": "success",
        "notifications": get_all_notifications(user_id=get_user_session().get('user_id'))
    }), 200

@user.route('/api/user/notification/<int:notification_id>/read', methods=['POST'])
@login_required
#@swag_from('../docs/user/notification/mark_read.yaml')
def api_mark_notification_read(notification_id):
    read_notification(user_id=get_user_session().get('user_id'), notification_id=notification_id)
    return jsonify({
        "status": "success"
    }), 200

@user.route('/api/user/notification/<int:notification_id>/unread', methods=['POST'])
@login_required
#@swag_from('../docs/user/notification/mark_read.yaml')
def api_mark_notification_unread(notification_id):
    unread_notification(user_id=get_user_session().get('user_id'), notification_id=notification_id)
    return jsonify({
        "status": "success"
    }), 200

@user.route('/api/user/notification/global/<int:notification_id>/read', methods=['POST'])
@login_required
#@swag_from('../docs/user/notification/mark_read.yaml')
def api_mark_global_notification_read(notification_id):
    read_global_notification(user_id=get_user_session().get('user_id'), global_notification_id=notification_id)
    return jsonify({
        "status": "success"
    }), 200

@user.route('/api/user/notification/global/<int:notification_id>/unread', methods=['POST'])
@login_required
#@swag_from('../docs/user/notification/mark_read.yaml')
def api_mark_global_notification_unread(notification_id):
    unread_global_notification(user_id=get_user_session().get('user_id'), global_notification_id=notification_id)
    return jsonify({
        "status": "success"
    }), 200

@user.route('/api/user/challenge/<int:challenge_id>/launch', methods=['POST'])
@login_required
#@swag_from('../docs/user/challenge/instance_launch.yaml')
def api_launch_challenge(challenge_id):
    result = launch_instance_for_user(user_id=get_user_session().get('user_id'), challenge_id=challenge_id)
    return jsonify({
        "status": "success",
        "instance_url": result["url"],
        "instance_expires_at": result["expires_at"]
    }), 200

@user.route('/api/user/challenge/<int:challenge_id>/instance/stop', methods=['POST'])
@login_required
#@swag_from('../docs/user/challenge/instance_stop.yaml')
def api_stop_challenge_instance(challenge_id):
    return jsonify({
        "status": "success",
        "message": stop_instance_for_user(user_id=get_user_session().get('user_id'), challenge_id=challenge_id)
    }), 200


@user.route('/api/user/challenge/<int:challenge_id>/files/list', methods=['GET'])
@login_required
#@swag_from('../docs/admin/challenge/files/challenge_files_list.yaml')
def api_list_challenge_files(challenge_id):
    return jsonify({
        "status": "success",
        "files": list_challenge_files(challenge_id)
    }), 200

@user.route('/api/user/boutique/<int:user_id>', methods=['GET'])
# @login_required
#@swag_from('../docs/user/boutique/list.yaml')
def api_list_boutique(user_id):
    return jsonify({
        "status": "success",
        "boutique": get_active_boutique(user_id=user_id)
    }), 200

