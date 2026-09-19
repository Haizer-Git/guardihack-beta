from sqlalchemy import and_, func, not_, or_, and_, case, inspect
from werkzeug.exceptions import BadRequest, Conflict, NotFound, InternalServerError
from extensions import db
from sqlalchemy.orm import joinedload
import os
from datetime import datetime
from core.security import (
    hash_flag, verify_flag, generate_token,
    file_sha256, encrypt_flag, decrypt_flag
)
from models.core import (
    User
)
from models.core.challenge import (
    Challenge, ChallengeSubmission, Category,
    ChallengeRotation, Rotation, ChallengeFiles,
    GeointConfig
)
from models.core.docker import(
    DockerImage,
    UserInstance
)

from services.score_service import (
    adjust_score, check_overtake
)
from services.xp_service import (
    adjust_xp
)
from services.upload_service import (
    upload_file, delete_file
)

XP_CHALLENGE_BASE = os.getenv("XP_CHALLENGE_BASE", 100)

AUTHORIZED_CHALLENGE_DIFFICULTY = {
    "INTRO": True,
    "EASY": True,
    "MEDIUM": True,
    "HARD": True,
    "EXPERT": True
}

AUTHORIZED_CHALLENGE_TYPE = {
    "PERMANENT": True,
    "ROTATION": True
}

AUTHORIZED_FLAG_TYPE = {
    "STATIC": True,
    "DYNAMIC": True
}

AUTHORIZED_FILTER_TYPE = {
    "ACTIVE": True,
    "NAME": True,
    "CATEGORY": True,
    "DIFFICULTY": True
}


def validate_challenge(user_id, challenge_id, flag):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise InternalServerError("USER_NOT_FOUND|L'utilisateur spécifié n'existe pas.")
    if not isinstance(challenge_id, int):
        raise BadRequest("INVALID_CHALLENGE_ID|L'ID du challenge doit être un entier.")
    challenge = (Challenge.query.filter_by(id=challenge_id).options(joinedload(Challenge.category),joinedload(Challenge.rotations).joinedload(ChallengeRotation.rotation),
                joinedload(Challenge.submissions).joinedload(ChallengeSubmission.user)
                )
                .first())
    if not challenge:
        raise NotFound("CHALLENGE_NOT_FOUND|Challenge non trouvé.")
    is_validated = ChallengeSubmission.query.filter_by(user_id=user_id, challenge_id=challenge_id, is_correct=True).with_entities(ChallengeSubmission.id).first()
    if is_validated:
        raise BadRequest("CHALLENGE_ALREADY_VALIDATED|Vous avez déjà validé ce challenge.")
    if not challenge.is_active:
        raise BadRequest("CHALLENGE_NOT_ACTIVE|Le challenge n'est pas actif actuellement.")
    result, type = verify_flag(stored_hash=challenge.master_flag, provided_flag=flag, dynamic={"user":user.secret_key, "challenge":challenge.secret_key} if challenge.flag_type=="DYNAMIC" else False)
    if not result:
        user_submission = ChallengeSubmission()
        user_submission.user_id = user_id
        user_submission.challenge_id = challenge_id
        user_submission.flag_submitted = flag
        user_submission.is_correct = False
        user_submission.flag_type = None
        user_submission.timestamp = datetime.now()
        db.session.add(user_submission)
        db.session.commit()
        raise BadRequest("FLAG_INCORRECT|Le flag soumis est incorrect.")
    user_submission = ChallengeSubmission()
    user_submission.user_id = user_id
    user_submission.challenge_id = challenge_id
    user_submission.flag_submitted = None
    user_submission.is_correct = True
    user_submission.flag_type = type
    user_submission.timestamp = datetime.now()
    db.session.add(user_submission)
    db.session.commit()
    user_level = user.level
    old_score = user.global_score
    new_score = adjust_score(user_id=user_id, score_change=challenge.points, history=True, reason=f"Validation du challenge {challenge.name}")
    # check_overtake(user_id=user_id, old_score=old_score, new_score=new_score)
    xp_change = adjust_xp(user_id=user_id, xp_change=XP_CHALLENGE_BASE, challenge_difficulty=challenge.difficulty)
    db.session.refresh(user)
    user.xp = User.query.filter_by(id=user.id).with_entities(User.xp).scalar()
    completion_info = {
        "challenge_id": challenge.id,
        "challenge_name": challenge.name,
        "points_awarded": challenge.points,
        "xp_awarded": xp_change,
        "category_id": challenge.category.id if challenge.category else None,
        "level_up": user.level > user_level,
    }
    return completion_info, f"Challenge {challenge.name} validé avec succès!"

def create_challenge(user_id, data):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    if not isinstance(data, dict):
        raise BadRequest("INVALID_DATA|Les données doivent être un dictionnaire.")
    user = User.query.filter_by(id=user_id).with_entities(User.id).first()
    if not user:
        raise InternalServerError("USER_NOT_FOUND|Utilisateur non trouvé.")
    required_fields = ['name', 'type', 'description', 'category_id', 'difficulty', 'points', 'flag_type', 'master_flag']
    for field in required_fields:
        if not data.get(field):
            raise BadRequest(f"MISSING_FIELD|Le champ '{field}' est requis.")
    name = data.get('name')
    type = data.get('type')
    description = data.get('description')
    category_id = data.get('category_id')
    difficulty = data.get('difficulty')
    points = data.get('points')
    docker_image_id = data.get('docker_image_id')
    flag_type = data.get('flag_type')
    master_flag = data.get('master_flag')
    external_url = data.get('external_url')
    geoint_config_id = data.get('geoint_config_id')
    access_methods_provided = sum([bool(docker_image_id), bool(external_url), bool(geoint_config_id)])
    if access_methods_provided > 1:
        raise BadRequest("INVALID_ACCESS_CONFIG|Vous ne pouvez configurer qu'un seul type d'accès à la fois.")
    existing_challenge = Challenge.query.filter_by(name=name).with_entities(Challenge.name).first()
    if existing_challenge:
        raise Conflict("CHALLENGE_ALREADY_EXISTS|Un challenge avec ce nom existe déjà.")
    if not isinstance(category_id, int):
        raise BadRequest("INVALID_CATEGORY_ID|L'ID de la catégorie doit être un entier.")
    category = Category.query.filter_by(id=category_id).with_entities(Category.id).first()
    if not category:
        raise NotFound("CATEGORY_NOT_FOUND|Catégorie de challenge non trouvée.")
    if not isinstance(difficulty, str) or not AUTHORIZED_CHALLENGE_DIFFICULTY.get(difficulty):
        raise BadRequest("INVALID_DIFFICULTY|Difficulté de challenge invalide.")
    if not isinstance(type, str) or not AUTHORIZED_CHALLENGE_TYPE.get(type):
        raise BadRequest("INVALID_TYPE|Type de challenge invalide.")
    if not isinstance(flag_type, str) or not AUTHORIZED_FLAG_TYPE.get(flag_type):
        raise BadRequest("INVALID_FLAG_TYPE|Type de flag invalide.")
    if not isinstance(points, int):
        raise BadRequest("INVALID_POINTS|Le nombre de points doit être un entier.")
    if docker_image_id is not None:
        if not isinstance(docker_image_id, int):
            raise BadRequest("INVALID_DOCKER_IMAGE_ID|L'ID de l'image Docker doit être un entier.")
        docker_image = DockerImage.query.filter_by(id=docker_image_id).with_entities(DockerImage.id).first()
        if not docker_image:
            raise NotFound("DOCKER_IMAGE_NOT_FOUND|Image Docker non trouvée.")
    if geoint_config_id is not None:
        if not isinstance(geoint_config_id, int):
            raise BadRequest("INVALID_GEOINT_CONFIG_ID|L'ID de la configuration GeoInt doit être un entier.")
        geoint_config = GeointConfig.query.filter_by(id=geoint_config_id).with_entities(GeointConfig.id).first()
        if not geoint_config:
            raise NotFound("GEOINT_CONFIG_NOT_FOUND|Configuration GeoInt non trouvée.")
    new_challenge = Challenge()
    new_challenge.name = name
    new_challenge.type = type
    new_challenge.description = description
    new_challenge.category_id = category_id
    new_challenge.difficulty = difficulty
    new_challenge.points = points
    new_challenge.docker_image_id = docker_image_id
    new_challenge.external_url = external_url
    new_challenge.geoint_config_id = geoint_config_id
    new_challenge.flag_type = flag_type
    new_challenge.master_flag = hash_flag(master_flag)
    new_challenge.encrypted_flag = encrypt_flag(master_flag)
    new_challenge.hidden = True
    new_challenge.created_by = user_id
    new_challenge.secret_key = generate_token()
    db.session.add(new_challenge)
    db.session.commit()
    return "Challenge créé avec succès."

def modify_challenge(challenge_id, data):
    if not isinstance(challenge_id, int):
        raise BadRequest("INVALID_CHALLENGE_ID|L'ID du challenge doit être un entier.")
    if not isinstance(data, dict):
        raise BadRequest("INVALID_DATA|Les données doivent être un dictionnaire.")
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        raise NotFound("CHALLENGE_NOT_FOUND|Challenge non trouvé.")
    modification = False
    if "new_name" in data:
        new_name = data['new_name']
        if challenge.name != new_name:
            existing_challenge = Challenge.query.filter(Challenge.name == new_name, Challenge.id != challenge_id).with_entities(Challenge.id).first()
            if existing_challenge:
                raise Conflict("CHALLENGE_ALREADY_EXISTS|Un challenge avec ce nom existe déjà.")
            challenge.name = new_name
            modification = True
    if "new_type" in data:
        new_type = data['new_type']
        if not isinstance(new_type, str) or not AUTHORIZED_CHALLENGE_TYPE.get(new_type):
            raise BadRequest("INVALID_TYPE|Type de challenge invalide.")
        if challenge.type != new_type:
            if new_type == "PERMANENT":
                challenge_rotations = ChallengeRotation.query.filter_by(challenge_id=challenge_id).all()
                for cr in challenge_rotations:
                    db.session.delete(cr)
            challenge.type = new_type
            modification = True
    if "new_description" in data:
        if challenge.description != data['new_description']:
            challenge.description = data['new_description']
            modification = True
    if "new_category_id" in data:
        new_category_id = data['new_category_id']
        if not isinstance(new_category_id, int):
            raise BadRequest("INVALID_CATEGORY_ID|L'ID de la catégorie doit être un entier.")
        if challenge.category_id != new_category_id:
            category = Category.query.filter_by(id=new_category_id).with_entities(Category.id).first()
            if not category:
                raise NotFound("CATEGORY_NOT_FOUND|Catégorie de challenge non trouvée.")
            challenge.category_id = new_category_id
            modification = True
    if "new_difficulty" in data:
        new_difficulty = data['new_difficulty']
        if not isinstance(new_difficulty, str) or not AUTHORIZED_CHALLENGE_DIFFICULTY.get(new_difficulty):
            raise BadRequest("INVALID_DIFFICULTY|Difficulté de challenge invalide.")
        if challenge.difficulty != new_difficulty:
            challenge.difficulty = new_difficulty
            modification = True
    if "new_points" in data:
        new_points = data['new_points']
        if not isinstance(new_points, int):
            raise BadRequest("INVALID_POINTS|Le nombre de points doit être un entier.")
        if challenge.points != new_points:
            challenge.points = new_points
            modification = True
    if "new_docker_image_id" in data or "new_external_url" in data or "new_geoint_config_id" in data:
        new_docker_id = data.get('new_docker_image_id', challenge.docker_image_id)
        new_ext_url = data.get('new_external_url', challenge.external_url)
        new_geoint_id = data.get('new_geoint_config_id', challenge.geoint_config_id)
        access_methods_provided = sum([bool(new_docker_id), bool(new_ext_url), bool(new_geoint_id)])
        if access_methods_provided > 1:
            raise Conflict("ACCESS_CONFLICT|Vous ne pouvez configurer qu'un seul type doperation/accès à la fois (Docker, URL externe ou GeoInt).")
        if new_docker_id is not None and new_docker_id != challenge.docker_image_id:
            if not isinstance(new_docker_id, int):
                raise BadRequest("INVALID_DOCKER_IMAGE_ID|L'ID de l'image Docker doit être un entier.")
            docker_image = DockerImage.query.filter_by(id=new_docker_id).with_entities(DockerImage.id).first()
            if not docker_image:
                raise NotFound("DOCKER_IMAGE_NOT_FOUND|Image Docker non trouvée.")
            challenge.docker_image_id = new_docker_id
            modification = True
        if new_ext_url is not None and new_ext_url != challenge.external_url:
            if not isinstance(new_ext_url, str):
                raise BadRequest("INVALID_EXTERNAL_URL|L'URL externe doit être une chaîne.")
            challenge.external_url = new_ext_url
            modification = True
        if new_geoint_id is not None and new_geoint_id != challenge.geoint_config_id:
            if not isinstance(new_geoint_id, int):
                raise BadRequest("INVALID_GEOINT_CONFIG_ID|L'ID de la configuration GeoInt doit être un entier.")
            geoint_config = GeointConfig.query.filter_by(id=new_geoint_id).with_entities(GeointConfig.id).first()
            if not geoint_config:
                raise NotFound("GEOINT_CONFIG_NOT_FOUND|Configuration GeoInt non trouvée.")
            challenge.geoint_config_id = new_geoint_id
            modification = True
    if "new_flag_type" in data:
        new_flag_type = data['new_flag_type']
        if not isinstance(new_flag_type, str) or not AUTHORIZED_FLAG_TYPE.get(new_flag_type):
            raise BadRequest("INVALID_FLAG_TYPE|Type de flag invalide.")
        if challenge.flag_type != new_flag_type:
            challenge.flag_type = new_flag_type
            modification = True
            challenge.external_url = new_ext_url
            challenge.geoint_config_id = new_geoint_id
            modification = True
    if "new_flag_type" in data:
        new_flag_type = data['new_flag_type']
        if not isinstance(new_flag_type, str) or not AUTHORIZED_FLAG_TYPE.get(new_flag_type):
            raise BadRequest("INVALID_FLAG_TYPE|Type de flag invalide.")
        if challenge.flag_type != new_flag_type:
            challenge.flag_type = new_flag_type
            modification = True
    if "new_master_flag" in data:
        new_master_flag = data['new_master_flag']
        if new_master_flag != decrypt_flag(challenge.encrypted_flag):
            challenge.master_flag = hash_flag(new_master_flag)
            challenge.encrypted_flag = encrypt_flag(new_master_flag)
            modification = True
    if modification == True:
        db.session.commit()
        return "Challenge modifié avec succès."
    else:
        raise BadRequest("NO_MODIFICATIONS|Aucune modification n'a été apporté au challenge.")

def delete_challenge(challenge_id):
    if not isinstance(challenge_id, int):
        raise BadRequest("INVALID_CHALLENGE_ID|L'ID du challenge doit être un entier.")
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        raise NotFound("CHALLENGE_NOT_FOUND|Challenge non trouvé.")
    challenge_submissions = ChallengeSubmission.query.filter_by(challenge_id=challenge_id).all()
    for submission in challenge_submissions:
        db.session.delete(submission)
    challenges_files = ChallengeFiles.query.filter_by(challenge_id=challenge_id).all()
    for file in challenges_files:
        delete_file(file.file_url)
        db.session.delete(file)
    if challenge.type == "ROTATION":
        challenge_rotations = ChallengeRotation.query.filter_by(challenge_id=challenge_id).all()
        for cr in challenge_rotations:
            db.session.delete(cr)
    db.session.delete(challenge)
    db.session.commit()
    return "Challenge supprimé avec succès."

def visibility_challenge(challenge_id, hidden):
    if not isinstance(challenge_id, int):
        raise BadRequest("INVALID_CHALLENGE_ID|L'ID du challenge doit être un entier.")
    if not isinstance(hidden, bool):
        raise InternalServerError("INVALID_HIDDEN_VALUE|La valeur de visibilité doit être un booléen.")
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        raise NotFound("CHALLENGE_NOT_FOUND|Challenge non trouvé.")
    if challenge.hidden == hidden:
        if hidden == True:
            raise Conflict("CHALLENGE_ALREADY_ACTIVE|Le challenge est déjà caché.")
        raise Conflict("CHALLENGE_ALREADY_HIDDEN|Le challenge est déjà actif.")
    challenge.hidden = hidden
    db.session.commit()
    return f"Le challenge '{challenge.name}' est maintenant {'caché' if hidden else 'visible'}."

def create_challenge_category(data):
    required_fields = ['category_name', 'category_description']
    for field in required_fields:
        if not data.get(field):
            raise BadRequest(f"MISSING_FIELD|Le champ '{field}' est requis pour créer une catégorie de challenge.")
    categories = Category.query.filter_by(name=data['category_name']).with_entities(Category.name).first()
    if categories:
        raise Conflict("CATEGORY_ALREADY_EXISTS|Une catégorie de challenge avec ce nom existe déjà.")
    new_category = Category()
    new_category.name = data['category_name']
    new_category.description = data['category_description']
    db.session.add(new_category)
    db.session.commit()
    return f"Catégorie {new_category.name} créée avec succès."

def delete_challenge_category(category_id):
    if not isinstance(category_id, int):
        raise BadRequest("INVALID_CATEGORY_ID|L'ID de la catégorie doit être un entier.")
    category = Category.query.filter_by(id=category_id).first()
    if not category:
        raise NotFound("CATEGORY_NOT_FOUND|Catégorie de challenge non trouvée.")
    challenges_in_category = Challenge.query.filter_by(category_id=category_id).with_entities(Challenge.id).first()
    if challenges_in_category:
        raise Conflict("CATEGORY_NOT_EMPTY|La catégorie contient des challenges et ne peut pas être supprimée.")
    db.session.delete(category)
    db.session.commit()
    return "Catégorie de challenge supprimée avec succès."

def list_challenge_category():
    results = Category.query.all()
    category_list = []
    for category in results:
        category_list.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
        })
    return category_list

def admin_list_category():
    results = (db.session.query(Category,
            func.count(Challenge.id).label('challenge_count'),
            func.sum(case((Challenge.type == 'ROTATION', 1), else_=0)).label('rotation_count'),
            func.sum(case((Challenge.type == 'PERMANENT', 1), else_=0)).label('permanent_count')
        )
        .outerjoin(Challenge, Category.id == Challenge.category_id)
        .group_by(Category.id)
        .all()
    )
    category_list = []
    for category, count, rotation_count, permanent_count in results:
        category_list.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "challenge_count": count,
            "rotation_count": rotation_count or 0,
            "permanent_count": permanent_count or 0,
        })
    return category_list

def admin_list_challenge_category(category_id):
    if not isinstance(category_id, int):
        raise BadRequest("INVALID_CATEGORY_ID|L'ID de la catégorie doit être un entier.")
    category = Category.query.filter_by(id=category_id).with_entities(Category.id).first()
    if not category:
        raise NotFound("CATEGORY_NOT_FOUND|Catégorie de challenge non trouvée.")
    challenges = Challenge.query.options(joinedload(Challenge.creator)).filter_by(category_id=category_id).all()
    list_challenge = []
    for challenge in challenges:
        list_challenge.append({
            "id": challenge.id,
            "name": challenge.name,
            "type": challenge.type,
            "difficulty": challenge.difficulty,
            "points": challenge.points,
            "creator": challenge.creator.username
        })
    return list_challenge

def modify_challenge_category(category_id, data):
    if not isinstance(category_id, int):
        raise BadRequest("INVALID_CATEGORY_ID|L'ID de la catégorie doit être un entier.")
    category = Category.query.filter_by(id=category_id).first()
    if not category:
        raise NotFound("CATEGORY_NOT_FOUND|Catégorie de challenge non trouvée.")
    modification = False
    new_category_name = data.get('new_category_name')
    new_category_description = data.get('new_category_description')
    if new_category_name:
        existing_category = Category.query.filter(Category.name == new_category_name, Category.id != category_id).with_entities(Category.id).first()
        if existing_category:
            raise Conflict("CATEGORY_ALREADY_EXISTS|Une catégorie de challenge avec ce nom existe déjà.")
        category.name = new_category_name
        modification = True
    if new_category_description:
        category.description = new_category_description
        modification = True
    if modification :
        db.session.commit()
        return "Catégorie de challenge modifiée avec succès."
    else:
        raise BadRequest("NO_MODIFICATIONS|Aucune modification n'a été apportée à la catégorie.")

def create_rotation(data):
    required_fields = ['name', 'start', 'end']
    if not isinstance(data, dict):
        raise BadRequest("INVALID_DATA|Les données doivent être un dictionnaire.")
    for field in required_fields:
        if not data.get(field):
            raise BadRequest(f"MISSING_FIELD|Le champ '{field}' est requis.")
    rotation_name = data['name']
    rotation_start = data['start']
    rotation_end = data['end']
    rotation = Rotation.query.filter_by(name=rotation_name).with_entities(Rotation.name).first()
    if rotation:
        raise Conflict("ROTATION_ALREADY_EXISTS|Une rotation avec ce nom existe déjà.")
    try:
        rotation_start = datetime.fromisoformat(rotation_start.replace("Z", "+00:00"))
        rotation_end = datetime.fromisoformat(rotation_end.replace("Z", "+00:00"))
    except (BadRequest):
        raise BadRequest("INVALID_DATE_FORMAT|Format de date invalide.")
    if rotation_start >= rotation_end:
        raise BadRequest("INVALID_DATE_RANGE|La date de début doit être antérieure à la date de fin.")
    new_rotation = Rotation()
    new_rotation.name = rotation_name
    new_rotation.start_time = rotation_start
    new_rotation.end_time = rotation_end
    db.session.add(new_rotation)
    db.session.commit()
    return "Rotation créée avec succès."

def modify_rotation(rotation_id, data):
    if not isinstance(rotation_id, int):
        raise BadRequest("INVALID_ROTATION_ID|L'ID de la rotation doit être un entier.")
    rotation = Rotation.query.filter_by(id=rotation_id).first()
    if not rotation:
        raise NotFound("ROTATION_NOT_FOUND|Rotation non trouvée.")
    if not isinstance(data, dict):
        raise BadRequest("INVALID_DATA|Les données doivent être un dictionnaire.")
    modification = False
    if "new_name" in data:
        new_name = data['new_name']
        rotation_exists = Rotation.query.filter(Rotation.name == new_name, Rotation.id != rotation_id).with_entities(Rotation.id).first()
        if rotation_exists:
            raise Conflict("ROTATION_ALREADY_EXISTS|Une rotation avec ce nom existe déjà.")
        rotation.name = new_name
        modification = True
    final_start = rotation.start_time
    final_end = rotation.end_time
    dates_modified = False
    if "new_start" in data:
        try:
            final_start = datetime.fromisoformat(data['new_start'].replace("Z", "+00:00"))
            dates_modified = True
        except (BadRequest):
            raise BadRequest("INVALID_DATE_FORMAT|Format de date invalide pour la nouvelle date de début.")
    if "new_end" in data:
        try:
            final_end = datetime.fromisoformat(data['new_end'].replace("Z", "+00:00"))
            dates_modified = True
        except (BadRequest):
            raise BadRequest("INVALID_DATE_FORMAT|Format de date invalide pour la nouvelle date de fin.")
    if dates_modified:
        if final_start >= final_end:
            raise BadRequest("INVALID_DATE_RANGE|La date de début doit être antérieure à la date de fin.")
        rotation.start_time = final_start
        rotation.end_time = final_end
        modification = True
    if modification == True:
        db.session.commit()
        return "Rotation modifiée avec succès."
    else :
        raise BadRequest("NO_MODIFICATIONS|Aucune modification n'a été apportée à la rotation.")


def delete_rotation(rotation_id):
    if not isinstance(rotation_id, int):
        raise BadRequest("INVALID_ROTATION_ID|L'ID de la rotation doit être un entier.")
    rotation = Rotation.query.filter_by(id=rotation_id).first()
    if not rotation:
        raise NotFound("ROTATION_NOT_FOUND|Rotation non trouvée.")
    ChallengeRotation.query.filter_by(rotation_id=rotation_id).delete()
    db.session.delete(rotation)
    db.session.commit()
    return "Rotation supprimée avec succès."

def add_challenge_rotation(rotation_id, challenges):
    if not isinstance(rotation_id, int):
        raise BadRequest("INVALID_ROTATION_ID|L'ID de la rotation doit être un entier.")
    if isinstance(challenges, dict):
        challenges = challenges.get('challenge_id', [])
    else:
        challenges = challenges
    if not isinstance(challenges, list):
        raise BadRequest("INVALID_CHALLENGE_DATA|La liste des challenges doit être un tableau.")
    if len(challenges) == 0:
        raise BadRequest("EMPTY_CHALLENGE_LIST|La liste des challenges est vide.")
    target_rotation = Rotation.query.filter_by(id=rotation_id).first()
    if not target_rotation:
        raise NotFound("ROTATION_NOT_FOUND|Rotation non trouvée.")
    overlapping_challenges_query = (ChallengeRotation.query.join(Rotation, ChallengeRotation.rotation_id == Rotation.id).filter(Rotation.id != rotation_id).filter(Rotation.start_time <= target_rotation.end_time,Rotation.end_time >= target_rotation.start_time)
                                    .with_entities(ChallengeRotation.challenge_id)
                                    .all())
    conflicting_challenge_ids = {link.challenge_id for link in overlapping_challenges_query}
    existing_links = (ChallengeRotation.query.filter_by(rotation_id=rotation_id).with_entities(ChallengeRotation.challenge_id).all())
    challenges_in_rotation = {link.challenge_id for link in existing_links}
    added_count = 0
    for challenge_id in challenges:
        if not isinstance(challenge_id, int):
            raise BadRequest("INVALID_CHALLENGE_ID|L'ID du challenge doit être un entier.")
        challenge_exists = Challenge.query.filter_by(id=challenge_id).with_entities(Challenge.id, Challenge.type).first()
        if not challenge_exists:
            raise NotFound(f"CHALLENGE_NOT_FOUND|Challenge n°{challenge_id} non trouvé.")
        if challenge_id in challenges_in_rotation:
            continue
        if challenge_id in conflicting_challenge_ids:
            raise Conflict(f"CHALLENGE_DATE_CONFLICT|Le challenge n°{challenge_id} est déjà planifié dans une autre rotation sur la même période temporelle.")
        if challenge_exists.type != "ROTATION":
            raise BadRequest(f"CHALLENGE_TYPE_INVALID|Le challenge n°{challenge_id} n'est pas de type rotation et ne peut pas être ajouté à une rotation.")
        new_link = ChallengeRotation()
        new_link.challenge_id = challenge_id
        new_link.rotation_id = rotation_id
        db.session.add(new_link)
        added_count += 1
    if added_count > 0:
        db.session.commit()
        return f"{added_count} {'challenges' if added_count > 1 else 'challenge'} {'ajoutés' if added_count > 1 else 'ajouté'} à la rotation avec succès."
    raise Conflict("CHALLENGE_ALREADY_ADDED|Aucun challenge ajouté à la rotation, tous les challenges étaient déjà présents.")

def remove_challenge_rotation(rotation_id, challenges):
    if not isinstance(rotation_id, int):
        raise BadRequest("INVALID_ROTATION_ID|L'ID de la rotation doit être un entier.")
    if isinstance(challenges, dict):
        challenges = challenges.get('challenge_id', [])
    else:
        challenges = challenges
    if not isinstance(challenges, list):
        raise BadRequest("INVALID_CHALLENGE_DATA|La liste des challenges doit être un tableau.")
    if len(challenges) == 0:
        raise BadRequest("EMPTY_CHALLENGE_LIST|La liste des challenges est vide.")
    rotation = Rotation.query.filter_by(id=rotation_id).with_entities(Rotation.id).first()
    if not rotation:
        raise NotFound("ROTATION_NOT_FOUND|Rotation non trouvée.")
    existing_links = ChallengeRotation.query.filter(ChallengeRotation.rotation_id == rotation_id,ChallengeRotation.challenge_id.in_(challenges)).all()
    links_by_challenge_id = {link.challenge_id: link for link in existing_links}
    removed_count = 0
    for challenge_id in challenges:
        if not isinstance(challenge_id, int):
            raise BadRequest("INVALID_CHALLENGE_ID|L'ID du challenge doit être un entier.")
        if challenge_id in links_by_challenge_id:
            link_to_remove = links_by_challenge_id[challenge_id]
            db.session.delete(link_to_remove)
            removed_count += 1
    if removed_count > 0:
        db.session.commit()
        return f"{removed_count} {'challenges' if removed_count > 1 else 'challenge'} {'retirés' if removed_count > 1 else 'retiré'} de la rotation avec succès."
    raise Conflict("CHALLENGE_NEVER_ADDED|Aucun challenge retiré de la rotation, aucun des challenges spécifiés n'était présent dans la rotation.")


def get_challenge(user_id, type=None, filter=None):
    if not isinstance(user_id, int):
        raise BadRequest("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = User.query.options(
        joinedload(User.submissions),
        joinedload(User.instances)
    ).filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|L'utilisateur spécifié n'existe pas.")
    validate_challenge_ids = {sub.challenge_id for sub in user.submissions if sub.is_correct}
    active_inst = user.active_instance
    active_instance_challenge_id = active_inst.challenge_id if active_inst else None
    query = Challenge.query.options(
        joinedload(Challenge.category),
        joinedload(Challenge.rotations).joinedload(ChallengeRotation.rotation)
    ).filter(
        Challenge.hidden == False,
        Challenge.is_active == True
    )
    if not type:
        pass
    elif not AUTHORIZED_FILTER_TYPE.get(type.upper()):
        raise BadRequest("INVALID_TYPE|Type de filtre invalide.")
    elif type.upper() == "ACTIVE":
        query = query.filter(Challenge.is_active == True)
    elif type.upper() == "NAME":
        if not filter:
            raise BadRequest("MISSING_FILTER|Le nom recherché est requis.")
        query = query.filter(Challenge.name.ilike(f"%{filter}%"))
    elif type.upper() == "CATEGORY":
        if not filter:
            raise BadRequest("MISSING_FILTER|La catégorie recherchée est requise.")
        query = query.join(Category).filter(Category.name == filter)
    elif type.upper() == "DIFFICULTY":
        if not filter:
            raise BadRequest("MISSING_FILTER|La difficulté recherchée est requise.")
        query = query.filter(Challenge.difficulty == filter)
    else:
        raise BadRequest("INVALID_TYPE|Type de filtre invalide.")
    challenges = query.all()
    challenge_list = []
    for challenge in challenges:
        active_rot = next((cr.rotation for cr in challenge.rotations if cr.rotation and cr.rotation.is_active), None)
        is_current_active_instance = (active_instance_challenge_id == challenge.id)
        challenge_list.append({
            "id": challenge.id,
            "name": challenge.name,
            "type": challenge.type,
            "description": challenge.description,
            "category": {
                "name": challenge.category.name,
                "description": challenge.category.description
            },
            "difficulty": challenge.difficulty,
            "points": challenge.points,
            "is_active": challenge.is_active,
            "is_validated": challenge.id in validate_challenge_ids,
            "has_active_instance": is_current_active_instance,
            "active_instance": {
                "url": active_inst.url,
                "expires_at": active_inst.expires_at.strftime("%d/%m/%Y %H:%M:%S") if active_inst.expires_at else None
            } if is_current_active_instance and active_inst else None,
            "rotation": {
                "rotation_id": active_rot.id,
                "rotation_name": active_rot.name,
                "rotation_start": active_rot.start_time.strftime("%d/%m/%Y %H:%M:%S"),
                "rotation_end": active_rot.end_time.strftime("%d/%m/%Y %H:%M:%S")
            } if active_rot else None
        })
    return challenge_list


def get_challenge_info(user_id, challenge_id):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    if not isinstance(challenge_id, int):
        raise BadRequest("INVALID_CHALLENGE_ID|L'ID du challenge doit être un entier.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise InternalServerError("USER_NOT_FOUND|Utilisateur non trouvé.")
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        raise NotFound("CHALLENGE_NOT_FOUND|Challenge non trouvé.")
    rotation_start = None
    rotation_end = None
    if challenge.type != 'PERMANENT' and not challenge.hidden:
        active_rot = next((cr.rotation for cr in challenge.rotations if cr.rotation and cr.rotation.is_active), None)
        if active_rot:
            rotation_start = active_rot.start_time.strftime("%d/%m/%Y %H:%M:%S") if active_rot.start_time else None
            rotation_end = active_rot.end_time.strftime("%d/%m/%Y %H:%M:%S") if active_rot.end_time else None
        else:
            valid_rotations = [cr.rotation for cr in challenge.rotations if cr.rotation and cr.rotation.start_time]
            if valid_rotations:
                now = datetime.now()
                closest_rotation = min(valid_rotations, key=lambda r: abs(r.start_time - now))
                rotation_start = closest_rotation.start_time.strftime("%d/%m/%Y %H:%M:%S")
                rotation_end = closest_rotation.end_time.strftime("%d/%m/%Y %H:%M:%S") if closest_rotation.end_time else None
    is_validated = ChallengeSubmission.query.filter_by(
        user_id=user_id, 
        challenge_id=challenge_id, 
        is_correct=True
    ).with_entities(ChallengeSubmission.id).first() is not None
    active_instance = None
    has_other_instance = False
    inst = user.active_instance
    if inst:
        if inst.challenge_id == challenge_id:
            active_instance = {
                "url": inst.url,
                "created_at": inst.created_at,
                "expires_at": inst.expires_at
            }
        else:
            has_other_instance = True
    success_history = []
    submissions_history = sorted(challenge.submissions, key=lambda x: x.submitted_at, reverse=True)
    for submission in submissions_history:
        if submission.is_correct:
            username = submission.user.username if submission.user else "Utilisateur anonyme"
            success_history.append({
                "username": username,
                "submitted_at": submission.submitted_at.strftime("%d/%m/%Y %H:%M:%S"),
            })
    challenge_info = {
        "id": challenge.id,
        "name": challenge.name,
        "type": challenge.type,
        "description": challenge.description,
        "category": {
            "name": challenge.category.name if challenge.category else "Sans catégorie",
            "description": challenge.category.description if challenge.category else ""
        },
        "difficulty": challenge.difficulty,
        "points": challenge.points,
        "docker_image_id": challenge.docker_image_id if challenge.is_active else None,
        "external_url": challenge.external_url if challenge.is_active else None,
        "geoint_config_id": challenge.geoint_config_id if challenge.is_active else None,
        "is_active": challenge.is_active,
        "rotation_start": rotation_start,
        "rotation_end": rotation_end,
        "is_validated": is_validated,
        "success_history": success_history,
        "active_instance": active_instance,
        "has_other_instance": has_other_instance
    }
    return challenge_info

def get_admin_challenge_info(challenge_id):
    if not isinstance(challenge_id, int):
        raise BadRequest("INVALID_CHALLENGE_ID|L'ID du challenge doit être un entier.")
    challenge = (
        Challenge.query.options(
            joinedload(Challenge.category),
            joinedload(Challenge.creator),
            joinedload(Challenge.rotations).joinedload(ChallengeRotation.rotation)
        )
        .filter_by(id=challenge_id)
        .first()
    )
    if not challenge:
        raise NotFound("CHALLENGE_NOT_FOUND|Challenge non trouvé.")
    rotations_list = []
    active_rotation = None
    for cr in challenge.rotations:
        rot = cr.rotation
        if not rot:
            continue
        rot_data = {
            "id": rot.id,
            "name": rot.name,
            "start_time": rot.start_time.strftime("%d/%m/%Y %H:%M:%S") if rot.start_time else None,
            "end_time": rot.end_time.strftime("%d/%m/%Y %H:%M:%S") if rot.end_time else None,
            "is_active": rot.is_active
        }
        rotations_list.append(rot_data)
        if rot.is_active and not active_rotation:
            active_rotation = rot
    challenge_info = {
        "id": challenge.id,
        "name": challenge.name,
        "type": challenge.type,
        "description": challenge.description,
        "category_id": challenge.category.id if challenge.category else None,
        "category_name": challenge.category.name if challenge.category else None,
        "category_description": challenge.category.description if challenge.category else None,
        "difficulty": challenge.difficulty,
        "flag_type": challenge.flag_type,
        "points": challenge.points,
        "docker_image_id": challenge.docker_image_id if challenge.docker_image else None,
        "docker_image_name": challenge.docker_image.name if challenge.docker_image else None,
        "external_url": challenge.external_url,
        "geoint_config_id": challenge.geoint_config_id,
        "hidden": challenge.hidden,
        "is_active": challenge.is_active,
        "active_rotation_id": active_rotation.id if active_rotation else None,
        "rotations": rotations_list,
        "created_by": challenge.creator.username if challenge.creator else "Inconnu",
        "created_at": challenge.created_at.strftime("%d/%m/%Y %H:%M:%S") if challenge.created_at else None,
    }
    return challenge_info

def get_admin_challenge_list(offset=0, limit=25, search=None, difficulty=None, category=None, challenge_type=None, active=None, sort_by="name", sort_dir="asc"):
    if not isinstance(offset, int) or offset < 0:
        offset = 0
    if not isinstance(limit, int) or limit <= 0:
        limit = 25
    sub_count = (
        ChallengeSubmission.query
        .with_entities(ChallengeSubmission.challenge_id, func.count(ChallengeSubmission.id).label('total_subs'))
        .group_by(ChallengeSubmission.challenge_id)
        .subquery()
    )
    query = (
        Challenge.query
        .options(joinedload(Challenge.category), joinedload(Challenge.creator))
        .outerjoin(sub_count, Challenge.id == sub_count.c.challenge_id)
    )
    if search:
        query = query.filter(Challenge.name.ilike(f"%{search}%"))
    if difficulty:
        query = query.filter(Challenge.difficulty.ilike(difficulty))
    if category:
        query = query.join(Challenge.category).filter(Category.name.ilike(category))
    if challenge_type:
        query = query.filter(Challenge.type.ilike(challenge_type))
    if active is not None:
        is_active = str(active).lower() in ['true', '1', 'yes']
        query = query.filter(Challenge.is_active == is_active)
    counts_data = query.with_entities(
        func.count(Challenge.id),
        func.sum(case((func.upper(Challenge.type) == 'PERMANENT', 1), else_=0)),
        func.sum(case((func.upper(Challenge.type) == 'ROTATION', 1), else_=0))
    ).first()
    total_count, permanent_count, rotation_count = counts_data if counts_data else (0, 0, 0)
    total_items = {
        "total": total_count or 0,
        "permanent": permanent_count or 0,
        "rotation": rotation_count or 0
    }
    allowed_sorts = {
        "name": Challenge.name,
        "category_name": Category.name,
        "difficulty": Challenge.difficulty,
        "points": Challenge.points,
        "type": Challenge.type,
    }
    if sort_by == "category_name":
        query = query.outerjoin(Challenge.category)
        
    sort_column = allowed_sorts.get(sort_by, Challenge.name)
    if sort_dir == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    results = query.with_entities(Challenge, sub_count.c.total_subs).offset(offset).limit(limit).all()
    rotations_data = ChallengeRotation.query.with_entities(ChallengeRotation.challenge_id, ChallengeRotation.rotation_id).all()
    rotation_map = {}
    for challenge_id, rotation_id in rotations_data:
        if challenge_id not in rotation_map:
            rotation_map[challenge_id] = []
        rotation_map[challenge_id].append(rotation_id)
    challenge_list = []
    for challenge, total_subs in results:
        cat_name = challenge.category.name if challenge.category else "Sans catégorie"
        challenge_list.append({
            "id": challenge.id,
            "name": challenge.name,
            "type": challenge.type,
            "description": challenge.description,
            "category": cat_name,
            "category_name": cat_name,
            "difficulty": challenge.difficulty,
            "points": challenge.points,
            "hidden": challenge.hidden,
            "is_active": challenge.is_active,
            "rotations": rotation_map.get(challenge.id, []),
            "submissions_count": total_subs if total_subs is not None else 0,
            "created_at": challenge.created_at.isoformat() if challenge.created_at else None,
            "created_by": challenge.creator.username if challenge.creator else "Inconnu",
        })
    return total_items, challenge_list


def get_user_challenge(target_username):
    user = User.query.filter_by(username=target_username).with_entities(User.id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    submissions = (ChallengeSubmission.query.filter_by(user_id=user.id, is_correct=True).options(joinedload(ChallengeSubmission.challenge).joinedload(Challenge.category))
                .order_by(ChallengeSubmission.submitted_at.desc())
                .all())
    challenge_list = []
    for submission in submissions:
        challenge = submission.challenge
        if not challenge:
            continue
        challenge_list.append({
            "id": challenge.id,
            "name": challenge.name,
            "category_name": challenge.category.name,
            "category_description": challenge.category.description,
            "difficulty": challenge.difficulty,
            "points": challenge.points,
            "submitted_at": submission.submitted_at.strftime("%d/%m/%Y %H:%M:%S")
        })
    return challenge_list

def get_statistics(target_username):
    user = User.query.filter_by(username=target_username).with_entities(User.id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    user_id = user[0]
    categories = Category.query.with_entities(Category.name).all()
    category_stats = {cat.name: 0 for cat in categories}
    difficulty_stats = {diff: 0 for diff in AUTHORIZED_CHALLENGE_DIFFICULTY.keys()}
    category_counts = (db.session.query(Category.name, func.count(ChallengeSubmission.id)).join(Challenge, Challenge.category_id == Category.id)
                        .join(ChallengeSubmission, ChallengeSubmission.challenge_id == Challenge.id).filter(ChallengeSubmission.user_id == user_id, ChallengeSubmission.is_correct == True)
                        .group_by(Category.name).all())
    for cat_name, count in category_counts:
        category_stats[cat_name] = count
    difficulty_counts = (db.session.query(Challenge.difficulty, func.count(ChallengeSubmission.id)).join(ChallengeSubmission, ChallengeSubmission.challenge_id == Challenge.id)
                        .filter(ChallengeSubmission.user_id == user_id, ChallengeSubmission.is_correct == True)).group_by(Challenge.difficulty).all()
    for diff, count in difficulty_counts:
        if diff in difficulty_stats:
            difficulty_stats[diff] = count
    return {
        "category_stats": category_stats,
        "difficulty_stats": difficulty_stats
    }

def get_challenge_history(challenge_id, offset, limit=20):
    if not isinstance(challenge_id, int):
        raise BadRequest("INVALID_CHALLENGE_ID|L'ID du challenge doit être un entier.")
    challenge = Challenge.query.filter_by(id=challenge_id).with_entities(Challenge.id).first()
    if not challenge:
        raise NotFound("CHALLENGE_NOT_FOUND|Challenge non trouvé.")
    if not isinstance(offset, int) or offset < 0:
        raise BadRequest("INVALID_OFFSET|L'offset doit être un entier positif.")
    if not isinstance(limit, int) or limit <= 0:
        raise BadRequest("INVALID_LIMIT|La limite doit être un entier positif.")
    total_submissions = (ChallengeSubmission.query.filter_by(challenge_id=challenge_id).with_entities(func.count(ChallengeSubmission.id)).scalar())
    submissions = (ChallengeSubmission.query.filter_by(challenge_id=challenge_id).options(joinedload(ChallengeSubmission.user)).order_by(ChallengeSubmission.submitted_at.desc()).offset(offset).limit(limit).all())
    submission_list = []
    for sub in submissions:
        submission_list.append({
            "submission_id": sub.id,
            "user_id": sub.user_id,
            "username": sub.user.username,
            "is_correct": sub.is_correct,
            "flag_submitted": sub.flag_submitted if not sub.is_correct else None,
            "flag_type": sub.flag_type if sub.is_correct else None,
            "submitted_at": sub.submitted_at.strftime("%d/%m/%Y %H:%M:%S")
        })
    return total_submissions, submission_list

def list_challenge_rotations():
    results = (db.session.query(Rotation, func.count(ChallengeRotation.challenge_id).label('challenge_count')).outerjoin(ChallengeRotation, Rotation.id == ChallengeRotation.rotation_id).group_by(Rotation.id).all())
    rotation_list = []
    for rotation, challenge_count in results:
        rotation_list.append({
            "id": rotation.id,
            "name": rotation.name,
            "start_time": rotation.start_time.strftime("%d/%m/%Y %H:%M:%S"),
            "end_time": rotation.end_time.strftime("%d/%m/%Y %H:%M:%S"),
            "is_active": rotation.is_active,
            "challenge_count": challenge_count
        })
    return rotation_list

def get_rotation_info(rotation_id):
    if not isinstance(rotation_id, int):
        raise BadRequest("INVALID_ROTATION_ID|L'ID de la rotation doit être un entier.")
    rotation = Rotation.query.filter_by(id=rotation_id).first()
    if not rotation:
        raise NotFound("ROTATION_NOT_FOUND|Rotation non trouvée.")
    challenges = (Challenge.query.join(ChallengeRotation, Challenge.id == ChallengeRotation.challenge_id).filter(ChallengeRotation.rotation_id == rotation_id).options(joinedload(Challenge.category)).all())
    challenges_list = []
    for challenge in challenges:
        challenges_list.append({
            "id": challenge.id,
            "name": challenge.name,
            "type": challenge.type,
            "description": challenge.description,
            "category_name": challenge.category.name,
            "category_description": challenge.category.description,
            "difficulty": challenge.difficulty,
            "points": challenge.points,
            "hidden": challenge.hidden,
            "created_at": challenge.created_at.isoformat(),
            "created_by": challenge.creator.username
        })
    rotation_info = {
        "id": rotation.id,
        "name": rotation.name,
        "start_time": rotation.start_time.strftime("%d/%m/%Y %H:%M:%S"),
        "end_time": rotation.end_time.strftime("%d/%m/%Y %H:%M:%S"),
        "challenges": challenges_list
    }
    return rotation_info

def add_challenge_files(challenge_id, file, file_type, custom_name=None):
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        raise NotFound("CHALLENGE_NOT_FOUND|Challenge non trouvé.")
    sha256 = file_sha256(file)
    file.stream.seek(0)
    file.stream.seek(0, os.SEEK_END)
    file_size_bytes = file.stream.tell()
    file.stream.seek(0)
    def format_size(size):
        for unit in ['o', 'Ko', 'Mo', 'Go']:
            if size < 1024.0:
                return f"{size:.1f} {unit}" if unit != 'o' else f"{int(size)} {unit}"
            size /= 1024.0
        return f"{size:.1f} To"
    file_size_formatted = format_size(file_size_bytes)
    path, extension = upload_file(challenge_id, file, custom_name)
    final_saved_name = os.path.basename(path)
    new_file = ChallengeFiles()
    new_file.challenge_id = challenge_id
    new_file.file_type = extension
    new_file.file_name = final_saved_name
    new_file.file_url = path
    new_file.file_role = file_type
    new_file.sha256 = sha256
    new_file.file_size = file_size_formatted
    db.session.add(new_file)
    db.session.commit()
    return final_saved_name, "Fichier de challenge ajouté avec succès."

def remove_challenge_files(challenge_id, file_id):
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        raise NotFound("CHALLENGE_NOT_FOUND|Challenge non trouvé.")
    file_entry = ChallengeFiles.query.filter_by(id=file_id, challenge_id=challenge_id).first()
    if not file_entry:
        raise NotFound("FILE_NOT_FOUND|Fichier de challenge non trouvé.")
    db.session.delete(file_entry)
    db.session.commit()
    delete_file(file_entry.file_url)
    return "Fichier de challenge supprimé avec succès."

def list_challenge_files(challenge_id):
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        raise NotFound("CHALLENGE_NOT_FOUND|Challenge non trouvé.")
    if challenge.is_active == False:
        return []
    files = challenge.files
    if not files:
        raise NotFound("CHALLENGE_NOT_FOUND|Aucun fichier associé.")
    file_list = []
    for file in files:
        if file:
            file_list.append({
                "id": file.id,
                "file_type": file.file_type,
                "file_name": file.file_name,
                "file_url": file.file_url,
                "file_role": file.file_role,
                "sha256": file.sha256,
                "file_size": file.file_size,
                "uploaded_at": file.created_at.strftime("%d/%m/%Y %H:%M:%S")
            })
    return file_list

def admin_list_challenge_files(challenge_id):
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        raise NotFound("CHALLENGE_NOT_FOUND|Challenge non trouvé.")
    files = challenge.files
    if not files:
        raise NotFound("CHALLENGE_NOT_FOUND|Aucun fichier associé.")
    file_list = []
    for file in files:
        if file:
            file_list.append({
                "id": file.id,
                "file_type": file.file_type,
                "file_name": file.file_name,
                "file_url": file.file_url,
                "file_role": file.file_role,
                "sha256": file.sha256,
                "file_size": file.file_size,
                "uploaded_at": file.created_at.strftime("%d/%m/%Y %H:%M:%S")
            })
    return file_list

def reveal_challenge_flag(challenge_id):
    if not isinstance(challenge_id, int):
        raise BadRequest("INVALID_CHALLENGE_ID|L'ID du challenge doit être un entier.")
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        raise NotFound("CHALLENGE_NOT_FOUND|Challenge non trouvé.")
    return decrypt_flag(challenge.encrypted_flag)