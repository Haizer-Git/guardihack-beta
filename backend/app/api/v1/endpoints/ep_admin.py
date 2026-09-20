from services.achievement_service import (
    create_achievement, delete_achievement, modify_achievement,
    list_achievement, get_achievement_info, add_achievement_requirement,
    delete_achievement_requirement, add_achievement_reward,
    delete_achievement_reward
)
from services.automatisation_service import (
    auto_create_token
)
from werkzeug.exceptions import BadRequest
from flask import (
    Blueprint, request, jsonify
)
from services.session_service import (
    get_user_session
)
from .middleware.mid_auth import (
    admin_required
)
from services.preset_service import (
    create_preset, delete_preset, get_preset_by_id, 
    list_preset, get_admin_preset_users
)
from services.auth_service import (
    create_token, delete_token, list_tokens,
    get_token_by_id, send_token
)
from services.badge_service import (
    admin_list_badges, create_badge, list_badges, modify_badge,
    delete_badge, assign_badge
)
from services.user_service import (
    get_user_list_admin, admin_update_user_status, get_admin_user_info
)
from services.xp_service import (
    adjust_xp
)
from services.score_service import (
    adjust_score, get_admin_score_history
)
from services.notification_service import (
    list_global_notifications, send_notification, send_global_notification
)
from services.upload_service import (
    upload_icons, delete_icon, get_all_icons
)

from services.cosmetic_service import (
    create_cosmetic, list_cosmetics, modify_cosmetic,
    delete_cosmetic, assign_cosmetic, admin_list_cosmetics, 
    get_admin_user_cosmetics
)
from services.challenge_service import (
    create_challenge, delete_challenge, get_admin_challenge_list,
    modify_challenge, add_challenge_rotation, create_challenge_category,
    delete_challenge_category, list_challenge_category,
    modify_challenge_category, get_challenge_info, get_challenge_history,
    list_challenge_rotations, get_rotation_info, create_rotation,
    modify_rotation, delete_rotation, remove_challenge_rotation,
    visibility_challenge, add_challenge_files, remove_challenge_files,
    admin_list_challenge_files, reveal_challenge_flag, admin_list_category,
    get_admin_challenge_info, admin_list_challenge_category
)
from services.docker_service import (
    create_docker_image, modify_docker_image, delete_docker_image, 
    list_docker_images, get_docker_image
)
from services.instance_service import (
    launch_instance_for_user, list_instances, stop_instance_for_user
)

admin = Blueprint('admin', __name__)


@admin.route('/api/admin/preset/create', methods=['POST'])
@admin_required
def api_create_preset():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": create_preset(user_id=get_user_session().get('user_id'), data=data)
    }), 201


@admin.route('/api/admin/preset/<int:preset_id>/delete', methods=['POST'])
@admin_required
def api_delete_preset(preset_id):
    return jsonify({
        "status": "success",
        "message": delete_preset(preset_id=preset_id)
    }), 200

@admin.route('/api/admin/preset/list', methods=['GET'])
@admin_required
def api_list_presets():
    return jsonify({
        "status": "success",
        "presets": list_preset()
    }), 200

@admin.route('/api/admin/preset/<int:preset_id>/info', methods=['GET'])
@admin_required
def api_get_preset_info(preset_id):
    return jsonify({
        "status": "success",
        "preset": get_preset_by_id(preset_id=preset_id)
    }), 200

@admin.route('/api/admin/preset/<int:preset_id>/users', methods=['GET'])
@admin_required
def api_get_preset_users(preset_id):
    return jsonify({
        "status": "success",
        "users": get_admin_preset_users(preset_id=preset_id)
    }), 200

@admin.route('/api/admin/token/create', methods=['POST'])
@admin_required
def api_create_preset_token():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": create_token(user_id=get_user_session().get('user_id'), data=data)
    }), 201

@admin.route('/api/admin/token/<int:token_id>/delete', methods=['POST'])
@admin_required
def api_delete_preset_token(token_id):
    return jsonify({
        "status": "success",
        "message": delete_token(token_id=token_id)
    }), 200


@admin.route('/api/admin/token/list', methods=['GET'])
@admin_required
def api_list_preset_tokens():
    return jsonify({
        "status": "success",
        "tokens": list_tokens()
    }), 200

@admin.route('/api/admin/token/<int:token_id>/info', methods=['GET'])
@admin_required
def api_get_token_info(token_id):
    return jsonify({
        "status": "success",
        "token": get_token_by_id(token_id=token_id)
    }), 200

@admin.route('/api/admin/token/<int:token_id>/notify', methods=['POST'])
@admin_required
def api_notify_token(token_id):
    return jsonify({
        "status": "success",
        "message": send_token(token_id=token_id)
    }), 200

@admin.route('/api/admin/token/create/auto/<int:preset_id>/<string:send_flag>', methods=['POST'])
@admin_required
def api_auto_create_token(preset_id, send_flag):
    file = request.files.get('file')
    if not file:
        return jsonify({"status": "error", "message": "Aucun fichier CSV fourni."}), 400
    send = send_flag.lower() in ['true', '1', 'yes', 'on']
    return jsonify({
        "status": "success",
        "message": auto_create_token(user_id=get_user_session().get('user_id'),preset_id=preset_id,file=file,send=send)
    }), 201

@admin.route('/api/admin/badge/create', methods=['POST'])
@admin_required
def api_create_badge():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": create_badge(user_id=get_user_session().get('user_id'), badge_info=data)
    }), 201

@admin.route('/api/admin/icon/upload/<string:item_type>', methods=['POST'])
@admin_required
def api_upload_icon(item_type):
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({
            "status": "error",
            "slug": "MISSING_ICON",
            "message": "Aucun fichier fourni."
        }), 400
    return jsonify({
        "status": "success",
        "message": upload_icons(files=files, item_type=item_type)
    }), 201

@admin.route('/api/admin/icon/<int:icon_id>/delete', methods=['POST'])
@admin_required
def api_delete_icon(icon_id):
    return jsonify({
        "status": "success",
        "message": delete_icon(icon_id=icon_id)
    }), 200

@admin.route('/api/admin/icon/list', methods=['GET'])
@admin_required
def api_list_icons():
    return jsonify({
        "status": "success",
        "icons": get_all_icons()
    }), 200

@admin.route('/api/admin/icon/list/<string:item_type>', methods=['GET'])
@admin_required
def api_list_icons_type(item_type):
    return jsonify({
        "status": "success",
        "icons": get_all_icons(item_type=item_type)
    }), 200

@admin.route('/api/admin/badge/<int:badge_id>/modify', methods=['POST'])
@admin_required
def api_modify_badge(badge_id):
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": modify_badge(badge_id=badge_id, badge_info=data)
    }), 201

@admin.route('/api/admin/badge/<int:badge_id>/delete', methods=['POST'])
@admin_required
def api_delete_badge(badge_id):
    return jsonify({
        "status": "success",
        "message": delete_badge(badge_id=badge_id)
    }), 200

@admin.route('/api/admin/badge/list', methods=['GET'])
@admin_required
def api_list_badges():
    return jsonify({
        "status": "success",
        "badges": admin_list_badges()
    }), 200

@admin.route('/api/admin/badge/<int:badge_id>/assign', methods=['POST'])
@admin_required
def api_assign_badge(badge_id):
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": assign_badge(target_user_id=data.get('user_id'), badge_id=badge_id, assign=True)
    }), 200

@admin.route('/api/admin/badge/<int:badge_id>/unassign', methods=['POST'])
@admin_required
def api_unassign_badge(badge_id):
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": assign_badge(target_user_id=data.get('user_id'), badge_id=badge_id, assign=False)
    }), 200

@admin.route('/api/admin/xp/adjust', methods=['POST'])
@admin_required
def api_adjust_xp():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": adjust_xp(user_id=data.get('user_id'), xp_change=data.get('amount'), manual=True)
    }), 200

@admin.route('/api/admin/score/adjust', methods=['POST'])
@admin_required
def api_adjust_score():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": adjust_score(user_id=data.get('user_id'), score_change=data.get('amount'), admin_id=get_user_session().get('user_id'), history=data.get('history', False), reason=data.get('reason'), manual=True)
    }), 200

@admin.route('/api/admin/score/<int:user_id>/history', methods=['GET'])
@admin_required
def api_get_score_history(user_id):
    return jsonify({
        "status": "success",
        "history": get_admin_score_history(user_id=user_id)
    }), 200

@admin.route('/api/admin/cosmetic/create', methods=['POST'])
@admin_required
def api_create_cosmetic():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": create_cosmetic(user_id=get_user_session().get('user_id'), cosmetic_info=data)
    }), 201

@admin.route('/api/admin/cosmetic/<int:cosmetic_id>/modify', methods=['POST'])
@admin_required
def api_modify_cosmetic(cosmetic_id):
    data = request.get_json()
    return jsonify({
        "status": "success",
        "cosmetic_id": cosmetic_id,
        "message": modify_cosmetic(cosmetic_id=cosmetic_id, cosmetic_info=data)
    }), 201


@admin.route('/api/admin/cosmetic/<int:cosmetic_id>/delete', methods=['POST'])
@admin_required
def api_delete_cosmetic(cosmetic_id):
    return jsonify({
        "status": "success",
        "message": delete_cosmetic(cosmetic_id=cosmetic_id)
    }), 200

@admin.route('/api/admin/cosmetic/list', methods=['GET'])
@admin_required
def api_list_cosmetics():
    return jsonify({
        "status": "success",
        "cosmetics": admin_list_cosmetics()
    }), 200

@admin.route('/api/admin/cosmetic/<int:cosmetic_id>/assign', methods=['POST'])
@admin_required
def api_assign_cosmetic(cosmetic_id):
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": assign_cosmetic(target_user_id=data.get('user_id'), cosmetic_id=cosmetic_id, assign=True)
    }), 200

@admin.route('/api/admin/cosmetic/<int:cosmetic_id>/unassign', methods=['POST'])
@admin_required
def api_unassign_cosmetic(cosmetic_id):
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": assign_cosmetic(target_user_id=data.get('user_id'), cosmetic_id=cosmetic_id, assign=False)
    }), 200

@admin.route('/api/admin/notification/create', methods=['POST'])
@admin_required
def api_create_notification():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": send_notification(user_id=data.get('user_id'), title=data.get('title'), message=data.get('message'))
    }), 200

@admin.route('/api/admin/notification/global/create', methods=['POST'])
@admin_required
def api_create_global_notification():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": send_global_notification(title=data.get('title'), message=data.get('message'), debut=data.get('debut'), end=data.get('end'))
    }), 200

@admin.route('/api/admin/notification/global/list', methods=['GET'])
@admin_required
def api_list_global_notifications():
    return jsonify({
        "status": "success",
        "notifications": list_global_notifications()
    }), 200


@admin.route('/api/admin/challenge/create', methods=['POST'])
@admin_required
def api_create_challenge():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": create_challenge(user_id=get_user_session().get('user_id'), data=data)
    }), 201

@admin.route('/api/admin/challenge/<int:challenge_id>/history/<int:offset>', methods=['GET'])
@admin_required
def api_challenge_history(challenge_id, offset):
    total_submissions, submissions = get_challenge_history(challenge_id, offset)
    return jsonify({
        "status": "success",
        "total_submissions": total_submissions,
        "history": submissions
    }), 200

@admin.route('/api/admin/challenge/rotation/create', methods=['POST'])
@admin_required
def api_create_challenge_rotation():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": create_rotation(data=data)
    }), 201

@admin.route('/api/admin/challenge/rotation/<int:rotation_id>/modify', methods=['POST'])
@admin_required
def api_modify_challenge_rotation(rotation_id):
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": modify_rotation(rotation_id=rotation_id, data=data)
    }), 200

@admin.route('/api/admin/challenge/rotation/<int:rotation_id>/delete', methods=['POST'])
@admin_required
def api_delete_challenge_rotation(rotation_id):
    return jsonify({
        "status": "success",
        "message": delete_rotation(rotation_id=rotation_id)
    }), 200

@admin.route('/api/admin/challenge/rotation/<int:rotation_id>/add', methods=['POST'])
@admin_required
def api_add_challenge_rotation(rotation_id):
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": add_challenge_rotation(rotation_id=rotation_id, challenges=data)
    }), 201

@admin.route('/api/admin/challenge/rotation/<int:rotation_id>/remove', methods=['POST'])
@admin_required
def api_remove_challenge_rotation(rotation_id):
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": remove_challenge_rotation(rotation_id=rotation_id, challenges=data)
    }), 200

@admin.route('/api/admin/challenge/rotation/list', methods=['GET'])
@admin_required
def api_list_challenge_rotations():
    return jsonify({
        "status": "success",
        "rotations": list_challenge_rotations()
    }), 200


@admin.route('/api/admin/challenge/rotation/<int:rotation_id>/info/', methods=['GET'])
@admin_required
def api_challenge_rotation_info(rotation_id):
    return jsonify({
        "status": "success",
        "rotation": get_rotation_info(rotation_id=rotation_id)
    }), 200

@admin.route('/api/admin/challenge/<int:challenge_id>/modify', methods=['POST'])
@admin_required
def api_modify_challenge(challenge_id):
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": modify_challenge(challenge_id=challenge_id, data=data)
    }), 200

@admin.route('/api/admin/challenge/<int:challenge_id>/activate', methods=['POST'])
@admin_required
def api_activate_challenge(challenge_id):
    return jsonify({
        "status": "success",
        "message": visibility_challenge(challenge_id=challenge_id, hidden=False)
    }), 200

@admin.route('/api/admin/challenge/<int:challenge_id>/desactivate', methods=['POST'])
@admin_required
def api_desactivate_challenge(challenge_id):
    return jsonify({
        "status": "success",
        "message": visibility_challenge(challenge_id=challenge_id, hidden=True)
    }), 200

@admin.route('/api/admin/challenge/<int:challenge_id>/delete', methods=['POST'])
@admin_required
def api_delete_challenge(challenge_id):
    return jsonify({
        "status": "success",
        "message": delete_challenge(challenge_id=challenge_id)
    }), 200

@admin.route('/api/admin/challenge/list', methods=['GET'])
@admin_required
def api_list_challenges():
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', default=25, type=int)
    search = request.args.get('search', default=None)
    difficulty = request.args.get('difficulty', default=None)
    category = request.args.get('category', default=None)
    challenge_type = request.args.get('type', default=None)
    active = request.args.get('active', default=None)
    sort_by = request.args.get('sort_by', default='name')
    sort_dir = request.args.get('sort_dir', default='asc')
    total_challenges, challenge_list = get_admin_challenge_list(
        offset=offset, limit=limit, search=search,
        difficulty=difficulty, category=category, challenge_type=challenge_type,
        active=active,
        sort_by=sort_by, sort_dir=sort_dir
    )
    return jsonify({
        "status": "success",
        "total_challenges": total_challenges,
        "challenges": challenge_list
    }), 200

@admin.route('/api/admin/challenge/<int:challenge_id>/info', methods=['GET'])
@admin_required
def api_challenge_info(challenge_id):
    return jsonify({
        "status": "success",
        "challenge": get_admin_challenge_info(challenge_id=challenge_id)
    }), 200

@admin.route('/api/admin/challenge/category/create', methods=['POST'])
@admin_required
def api_create_challenge_category():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": create_challenge_category(data=data)
    }), 201

@admin.route('/api/admin/challenge/category/<int:category_id>/delete', methods=['POST'])
@admin_required
def api_delete_challenge_category(category_id):
    return jsonify({
        "status": "success",
        "message": delete_challenge_category(category_id=category_id)
    }), 200

@admin.route('/api/admin/challenge/category/list', methods=['GET'])
@admin_required
def api_list_challenge_category():
    return jsonify({
        "status": "success",
        "categories": admin_list_category()
    }), 200

@admin.route('/api/admin/challenge/category/<int:category_id>/challenges', methods=['GET'])
@admin_required
def api_list_challenge_in_category(category_id):
    return jsonify({
        "status": "success",
        "challenges": admin_list_challenge_category(category_id=category_id)
    }), 200

@admin.route('/api/admin/challenge/category/<int:category_id>/modify', methods=['POST'])
@admin_required
def api_modify_challenge_category(category_id):
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": modify_challenge_category(category_id=category_id, data=data)
    }), 200

@admin.route('/api/admin/docker/image/create', methods=['POST'])
@admin_required
def api_create_docker_image():
    image_info = {
        "name": request.form.get("name"),
        "tag": request.form.get("tag", "latest"),
        "internal_port": request.form.get("internal_port"),
        "memory_limit": request.form.get("memory_limit", "256m")
    }
    uploaded_file = request.files.get("file")
    if not uploaded_file or uploaded_file.filename == "":
        raise BadRequest("MISSING_FILE|Le fichier ZIP du challenge est obligatoire.")
    image_tag = create_docker_image(image_info=image_info, zip_file=uploaded_file)
    return jsonify({
        "status": "success",
        "message": f"Image {image_tag} créée et buildée avec succès !"
    }), 201

@admin.route('/api/admin/docker/image/<int:image_id>/modify', methods=['POST'])
@admin_required
def api_modify_docker_image(image_id):
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": modify_docker_image(image_id=image_id, image_info=data)
    }), 200

@admin.route('/api/admin/docker/image/<int:image_id>/delete', methods=['POST'])
@admin_required
def api_delete_docker_image(image_id):
    return jsonify({
        "status": "success",
        "message": delete_docker_image(image_id=image_id)
    }), 200

@admin.route('/api/admin/docker/image/<int:image_id>/info', methods=['GET'])
@admin_required
def api_get_docker_image_info(image_id):
    return jsonify({
        "status": "success",
        "image": get_docker_image(image_id=image_id)
    }), 200

@admin.route('/api/admin/docker/image/list', methods=['GET'])
@admin_required
def api_list_docker_images():
    return jsonify({
        "status": "success",
        "images": list_docker_images()
    }), 200


@admin.route('/api/admin/docker/instance/launch', methods=['POST'])
@admin_required
def api_launch_docker_instance():
    data = request.get_json()
    launch_instance_for_user(user_id=data.get('user_id'), challenge_id=data.get('challenge_id'))
    return jsonify({
        "status": "success",
        "message": "Instance Docker lancée avec succès !"
    }), 200

@admin.route('/api/admin/docker/instance/stop', methods=['POST'])
@admin_required
def api_stop_docker_instance():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": stop_instance_for_user(user_id=data.get('user_id'), challenge_id=data.get('challenge_id'))
    }), 200

@admin.route('/api/admin/docker/instance/list', methods=['GET'])
@admin_required
def api_list_docker_instances():
    return jsonify({
        "status": "success",
        "instances": list_instances()
    }), 200

@admin.route('/api/admin/user/<int:user_id>/cosmetic/list', methods=['GET'])
@admin_required
def api_list_user_cosmetics(user_id):
    return jsonify({
        "status": "success",
        "cosmetics": get_admin_user_cosmetics(user_id=user_id)
    }), 200

@admin.route('/api/admin/user/list', methods=['GET'])
@admin_required
def api_get_user_list():
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 25, type=int)
    search = request.args.get('search', type=str)
    role = request.args.get('role', type=str)
    affiliation = request.args.get('affiliation', type=str)
    status = request.args.get('status', type=str)
    connected_param = request.args.get('connected', type=str)
    connected = True if connected_param and connected_param.lower() == 'true' else None
    sort_by = request.args.get('sort_by', 'id', type=str)
    sort_dir = request.args.get('sort_dir', 'desc', type=str)
    total_users, users = get_user_list_admin(
        offset=offset, 
        limit=limit, 
        search=search, 
        role=role, 
        affiliation=affiliation, 
        status=status,
        connected=connected,
        sort_by=sort_by, 
        sort_dir=sort_dir
    )
    return jsonify({
        "status": "success",
        "total_users": total_users,
        "users": users
    }), 200

@admin.route('/api/admin/user/<int:user_id>/info', methods=['GET'])
@admin_required
def api_get_user_info(user_id):
    return jsonify({
        "status": "success",
        "user": get_admin_user_info(user_id=user_id)
    }), 200


@admin.route('/api/admin/user/<int:user_id>/status/update', methods=['POST'])
@admin_required
def api_update_user_status(user_id):
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": admin_update_user_status(user_id=user_id, new_status=data.get('new_status'), reason=data.get('reason'), ended_at=data.get('ended_at'), admin_id=get_user_session().get('user_id'))
    }), 200


@admin.route('/api/admin/challenge/<int:challenge_id>/files/add', methods=['POST'])
@admin_required
def api_add_challenge_files(challenge_id):
    if 'file' not in request.files:
        return jsonify({
            "status": "error",
            "slug": "MISSING_FILE",
            "message": "Fichier manquant."
        }), 400
    file_name = request.form.get('file_name')
    file_type = request.form.get('file_type')
    if not file_type:
        return jsonify({
            "status": "error",
            "slug": "MISSING_FILE_TYPE",
            "message": "Type de fichier manquant"
        }), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            "status": "error",
            "slug": "EMPTY_FILE",
            "message": "Le fichier est vide"
        }), 400
    path, message = add_challenge_files(challenge_id, file, file_type, custom_name=file_name)
    return jsonify({
        "status": "success",
        "message": message,
        "file_name": path
    }), 201

@admin.route('/api/admin/challenge/<int:challenge_id>/files/<int:file_id>/remove', methods=['POST'])
@admin_required
def api_remove_challenge_files(challenge_id, file_id):
    return jsonify({
        "status": "success",
        "message": remove_challenge_files(challenge_id=challenge_id, file_id=file_id)
    }), 200

@admin.route('/api/admin/challenge/<int:challenge_id>/files/list', methods=['GET'])
@admin_required
def api_list_challenge_files(challenge_id):
    return jsonify({
        "status": "success",
        "files": admin_list_challenge_files(challenge_id)
    }), 200

@admin.route('/api/admin/challenge/<int:challenge_id>/reveal_flag', methods=['GET'])
@admin_required
def api_reveal_challenge_flag(challenge_id):
    return jsonify({
        "status": "success",
        "flag": reveal_challenge_flag(challenge_id)
    }), 200

@admin.route('/api/admin/achievement/create', methods=['POST'])
@admin_required
def api_create_achievement():
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": create_achievement(user_id=get_user_session().get('user_id'), name=data.get('name'), description=data.get('description'))
    }), 201

@admin.route('/api/admin/achievement/<int:achievement_id>/modify', methods=['POST'])
@admin_required
def api_modify_achievement(achievement_id):
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": modify_achievement(achievement_id=achievement_id, name=data.get('name'), description=data.get('description'))
    }), 200

@admin.route('/api/admin/achievement/<int:achievement_id>/delete', methods=['POST'])
@admin_required
def api_delete_achievement(achievement_id):
    return jsonify({
        "status": "success",
        "message": delete_achievement(achievement_id=achievement_id)
    }), 200

@admin.route('/api/admin/achievement/<int:achievement_id>/info', methods=['GET'])
@admin_required
def api_get_achievement_info(achievement_id):
    return jsonify({
        "status": "success",
        "message": get_achievement_info(achievement_id=achievement_id)
    }), 200

@admin.route('/api/admin/achievement/<int:achievement_id>/requirements/add', methods=['POST'])
@admin_required
def api_add_achievement_requirement(achievement_id):
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": add_achievement_requirement(achievement_id=achievement_id, requirements_list=data.get('requirements', []))
    }), 201

@admin.route('/api/admin/achievement/requirement/<int:requirement_id>/delete', methods=['POST'])
@admin_required
def api_delete_achievement_requirement(requirement_id):
    return jsonify({
        "status": "success",
        "message": delete_achievement_requirement(requirement_id=requirement_id)
    }), 200

@admin.route('/api/admin/achievement/<int:achievement_id>/reward/add', methods=['POST'])
@admin_required
def api_add_achievement_requirement_reward(achievement_id):
    data = request.get_json()
    return jsonify({
        "status": "success",
        "message": add_achievement_reward(achievement_id=achievement_id, rewards_list=data.get('rewards', []))
    }), 201

@admin.route('/api/admin/achievement/reward/<int:reward_id>/delete', methods=['POST'])
@admin_required
def api_delete_achievement_requirement_reward(reward_id):
    return jsonify({
        "status": "success",
        "message": delete_achievement_reward(reward_id=reward_id)
    }), 200

@admin.route('/api/admin/achievement/list', methods=['GET'])
@admin_required
def api_list_achievement():
    return jsonify({
        "status": "success",
        "message": list_achievement()
    }), 200
