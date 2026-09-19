from werkzeug.exceptions import NotFound, BadRequest, InternalServerError, Conflict

from extensions import db
from datetime import datetime
from models.core import (
    User, UserProfile, Cosmetic,
    UserCosmetic, Badge, UserBadge,
    Achievement, UserAchievement, AchievementRequirement,
    AchievementReward
)
from models.core.challenge import (
    ChallengeSubmission, Challenge
)

AUTHORIZED_REQUIREMENT_TYPES = {
    "CHALLENGE_COMPLETION": ["challenge_id"],
    "CHALLENGE_COMPLETION_COUNT": ["challenge_id", "count"],
    "CATEGORY_COMPLETION": ["category_id"],
    "CATEGORY_COMPLETION_COUNT": ["category_id", "count"],
    "COSMETIC_OWNERSHIP": ["cosmetic_id"],
    "COSMETIC_OWNERSHIP_COUNT": ["cosmetic_id", "count"],
    "BADGE_OWNERSHIP": ["badge_id"],
    "BADGE_OWNERSHIP_COUNT": ["badge_id", "count"],
    "POINTS_EARNED": ["count"],
    "LEVEL_REACHED": ["count"],
    "CONNECTION_DATE": ["target_date"],
    "CONNECTION_STREAK": ["count"],
}

FIELDS_TYPE_MAPPING = {
    "CHALLENGE_COMPLETION": {"challenge_id": int},
    "CHALLENGE_COMPLETION_COUNT": {"challenge_id": int, "count": int},
    "CATEGORY_COMPLETION": {"category_id": int},
    "CATEGORY_COMPLETION_COUNT": {"category_id": int, "count": int},
    "COSMETIC_EARNED": {"cosmetic_id": int},
    "COSMETIC_OWNERSHIP_COUNT": {"cosmetic_id": int, "count": int},
    "BADGE_EARNED": {"badge_id": int},
    "BADGE_OWNERSHIP_COUNT": {"badge_id": int, "count": int},
    "POINTS_EARNED": {"count": int},
    "LEVEL_REACHED": {"count": int},
    "CONNECTION_DATE": {"target_date": str},
    "CONNECTION_STREAK": {"count": int},
}

AUTHORIZED_REWARD_TYPES = {
    "COSMETIC": Cosmetic,
    "BADGE": Badge,
    "POINTS": True,
    "XP": True,
}

AUTHORIZED_ACTION_TYPES = {
    "CHALLENGE_COMPLETION": "Challenge",
    "BADGE_EARNED": "Badge",
    "COSMETIC_EARNED": "Cosmetic",
    "ACHIEVEMENT_UNLOCKED": "Achievement",
    "POINTS_EARNED": "Points",
    "LEVEL_REACHED": "Level",
    "CONNECTION_STREAK": "ConnectionStreak",
    "CONNECTION_DATE": "ConnectionDate",
}

REQUIREMENT_CONFIG = {
    "CHALLENGE_COMPLETION": {
        "model": ChallengeSubmission,
        "foreign_key": "challenge_id",
        "check": lambda user_id, req, val: ChallengeSubmission.query.filter_by(user_id=user_id, challenge_id=val, is_correct=True).first() is not None
    },
    "CHALLENGE_COMPLETION_COUNT": {
        "check": lambda user_id, req, val: ChallengeSubmission.query.filter_by(user_id=user_id, is_correct=True).count() >= req.count
    },
    "COSMETIC_OWNERSHIP": {
        "model": UserCosmetic,
        "foreign_key": "cosmetic_id",
        "check": lambda user_id, req, val: UserCosmetic.query.filter_by(user_id=user_id, cosmetic_id=val).first() is not None
    },
    "COSMETIC_OWNERSHIP_COUNT": {
        "check": lambda user_id, req, val: UserCosmetic.query.filter_by(user_id=user_id).count() >= req.count
    },
    "BADGE_OWNERSHIP": {
        "model": UserBadge,
        "foreign_key": "badge_id",
        "check": lambda user_id, req, val: UserBadge.query.filter_by(user_id=user_id, badge_id=val).first() is not None
    },
    "BADGE_OWNERSHIP_COUNT": {
        "check": lambda user_id, req, val: UserBadge.query.filter_by(user_id=user_id).count() >= req.count
    },
    "POINTS_EARNED": {
        "model": User,
        "check": lambda user_id, req, val: (u := User.query.get(user_id)) and u.global_score >= req.count
    },
    "LEVEL_REACHED": {
        "model": User,
        "check": lambda user_id, req, val: (u := User.query.get(user_id)) and u.level >= req.count
    },
    "CONNECTION_STREAK": {
        "model": User,
        "check": lambda user_id, req, val: (u := User.query.get(user_id)) and u.connection_streak >= req.count
    },
    "CONNECTION_DATE": {
        "model": User,
        "check": lambda user_id, req, val: (u := User.query.get(user_id)) and u.last_connection and req.target_date and u.last_connection.date() == req.target_date.date()
    },
    "CATEGORY_COMPLETION": {
        "check": lambda user_id, req, val: check_category_completion(user_id, req, completed=True)
    },
    "CATEGORY_COMPLETION_COUNT": {
        "check": lambda user_id, req, val: check_category_completion(user_id, req, completed=False)
    }
}


def create_achievement(user_id, name, description):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = User.query.filter_by(id=user_id).with_entities(User.id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    existing_achievement = Achievement.query.filter_by(name=name).first()
    if existing_achievement:
        raise Conflict("ACHIEVEMENT_EXISTS|Un achievement avec ce nom existe déjà.")
    new_achievement = Achievement()
    new_achievement.name = name
    new_achievement.description = description
    new_achievement.created_by = user_id
    db.session.add(new_achievement)
    db.session.commit()
    return "Achievement créé avec succès."

def delete_achievement(achievement_id):
    if not isinstance(achievement_id, int):
        raise BadRequest("INVALID_ACHIEVEMENT_ID|L'ID de l'achievement doit être un entier.")
    achievement = Achievement.query.filter_by(id=achievement_id).first()
    if not achievement:
        raise NotFound("ACHIEVEMENT_NOT_FOUND|Achievement non trouvé.")
    AchievementRequirement.query.filter_by(achievement_id=achievement_id).delete()
    db.session.delete(achievement)
    db.session.commit()
    return "Achievement supprimé avec succès."

def modify_achievement(achievement_id, name=None, description=None):
    if not isinstance(achievement_id, int):
        raise BadRequest("INVALID_ACHIEVEMENT_ID|L'ID de l'achievement doit être un entier.")
    achievement = Achievement.query.filter_by(id=achievement_id).first()
    if not achievement:
        raise NotFound("ACHIEVEMENT_NOT_FOUND|Achievement non trouvé.")
    if not name and not description:
        raise BadRequest("NO_MODIFICATION|Aucune modification n'a été apportée.")
    if name:
        existing_achievement = Achievement.query.filter_by(name=name).first()
        if existing_achievement and existing_achievement.id != achievement_id:
            raise Conflict("ACHIEVEMENT_EXISTS|Un achievement avec ce nom existe déjà.")
        achievement.name = name
    if description:
        achievement.description = description
    db.session.commit()
    return "Achievement modifié avec succès."

def list_achievement():
    achievements = Achievement.query.all()
    return [
        {
            "id": achievement.id,
            "name": achievement.name,
            "description": achievement.description,
            "created_by": achievement.created_by,
            "created_at": achievement.created_at,
            "requirement_count": len(achievement.requirements),
            "reward_count": len(achievement.rewards),
            "users_count": len(achievement.users)
        }
        for achievement in achievements
    ]

def get_achievement_info(achievement_id):
    if not isinstance(achievement_id, int):
        raise BadRequest("INVALID_ACHIEVEMENT_ID|L'ID de l'achievement doit être un entier.")
    achievement = Achievement.query.filter_by(id=achievement_id).first()
    if not achievement:
        raise NotFound("ACHIEVEMENT_NOT_FOUND|Achievement non trouvé.")
    return {
        "id": achievement.id,
        "name": achievement.name,
        "description": achievement.description,
        "created_by": achievement.created_by,
        "created_at": achievement.created_at,
        "requirements": [
            {
                "id": req.id,
                "type": req.type,
                "count": req.count,
                "target_date": req.target_date,
                "challenge_id": req.challenge_id,
                "category_id": req.category_id,
                "badge_id": req.badge_id,
                "cosmetic_id": req.cosmetic_id
            } for req in achievement.requirements
        ],
        "rewards": [
            {
                "id": reward.id,
                "type": reward.type,
                "value": reward.value
            } for reward in achievement.rewards
        ],
        "users": [
            {
                "id": user.id,
                "user_id": user.user_id,
                "username": user.user.username if hasattr(user, 'user') and user.user else None,
                "unlocked_at": user.unlocked_at.strftime("%d/%m/%Y %H:%M:%S") if user.unlocked_at else None,
                "is_read": user.is_read,
                "reward_claimed": user.reward_claimed
            } for user in achievement.users
        ]
    }

def add_achievement_requirement(achievement_id, requirements_list):
    if not isinstance(achievement_id, int):
        raise BadRequest("INVALID_ACHIEVEMENT_ID|L'ID de l'achievement doit être un entier.")
    achievement = Achievement.query.filter_by(id=achievement_id).first()
    if not achievement:
        raise NotFound("ACHIEVEMENT_NOT_FOUND|Achievement non trouvé.")
    if not isinstance(requirements_list, list) or len(requirements_list) == 0:
        raise BadRequest("INVALID_DATA|Une liste de prérequis est requise.")
    new_requirements = []
    for data in requirements_list:
        req_type = data.get("type")
        if req_type not in AUTHORIZED_REQUIREMENT_TYPES:
            raise BadRequest(f"INVALID_REQUIREMENT_TYPE|Type de requirement invalide: {req_type}")
        required_fields = AUTHORIZED_REQUIREMENT_TYPES[req_type]
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"MISSING_FIELD|Le champ '{field}' est requis pour le type '{req_type}'.")
        for field, expected_type in FIELDS_TYPE_MAPPING[req_type].items():
            if field in data and not isinstance(data[field], expected_type):
                raise BadRequest(f"INVALID_FIELD_TYPE|Le champ '{field}' doit être de type {expected_type.__name__}.")
        new_req = AchievementRequirement()
        new_req.achievement_id = achievement_id
        new_req.type = req_type
        new_req.count = data.get("count")
        target_date_str = data.get("target_date")
        if target_date_str:
            try:
                new_req.target_date = datetime.fromisoformat(target_date_str.replace("Z", "+00:00"))
            except ValueError:
                pass
        new_req.challenge_id = data.get("challenge_id")
        new_req.category_id = data.get("category_id")
        new_req.badge_id = data.get("badge_id")
        new_req.cosmetic_id = data.get("cosmetic_id")
        db.session.add(new_req)
        new_requirements.append(new_req)
    db.session.commit()
    return f"{len(new_requirements)} prérequis ajoutés avec succès."

def delete_achievement_requirement(requirement_id):
    if not isinstance(requirement_id, int):
        raise BadRequest("INVALID_REQUIREMENT_ID|L'ID du requirement doit être un entier.")
    requirement = AchievementRequirement.query.filter_by(id=requirement_id).first()
    if not requirement:
        raise NotFound("REQUIREMENT_NOT_FOUND|Requirement non trouvé.")
    db.session.delete(requirement)
    db.session.commit()
    return "Requirement supprimé avec succès."

def add_achievement_reward(achievement_id, rewards_list):
    if not isinstance(achievement_id, int):
        raise BadRequest("INVALID_ACHIEVEMENT_ID|L'ID de l'achievement doit être un entier.")
    achievement = Achievement.query.filter_by(id=achievement_id).first()
    if not achievement:
        raise NotFound("ACHIEVEMENT_NOT_FOUND|Achievement non trouvé.")
    if not isinstance(rewards_list, list) or len(rewards_list) == 0:
        raise BadRequest("INVALID_DATA|Une liste de récompenses est requise.")
    new_rewards = []
    for data in rewards_list:
        rew_type = data.get("type")
        if rew_type not in AUTHORIZED_REWARD_TYPES:
            raise BadRequest(f"INVALID_REWARD_TYPE|Type de reward invalide: {rew_type}")
        reward_id = data.get("reward_id")
        value = data.get("value")
        if rew_type in ["POINTS", "XP"]:
            if value is None or not isinstance(value, (int, float)):
                raise BadRequest("INVALID_REWARD_VALUE|Une valeur numérique est requise pour POINTS/XP.")
            new_rew = AchievementReward()
            new_rew.achievement_id = achievement_id
            new_rew.type = rew_type
            new_rew.value = value
        else:
            if reward_id is None or not isinstance(reward_id, int):
                raise BadRequest("INVALID_REWARD_ID|Un ID de récompense valide est requis.")
            model_class = AUTHORIZED_REWARD_TYPES[rew_type]
            reward_obj = model_class.query.filter_by(id=reward_id).first()
            if not reward_obj:
                raise NotFound(f"REWARD_NOT_FOUND|Item introuvable pour l'ID {reward_id}.")
            new_rew = AchievementReward()
            new_rew.achievement_id = achievement_id
            new_rew.type = rew_type
            new_rew.cosmetic_id = reward_id if rew_type == "COSMETIC" else None
            new_rew.badge_id = reward_id if rew_type == "BADGE" else None
        db.session.add(new_rew)
        new_rewards.append(new_rew)
    db.session.commit()
    return f"{len(new_rewards)} récompenses ajoutées avec succès."

def delete_achievement_reward(reward_id):
    if not isinstance(reward_id, int):
        raise BadRequest("INVALID_REWARD_ID|L'ID du reward doit être un entier.")
    reward = AchievementReward.query.filter_by(id=reward_id).first()
    if not reward:
        raise NotFound("REWARD_NOT_FOUND|Reward non trouvé pour cet achievement.")
    db.session.delete(reward)
    db.session.commit()
    return "Reward supprimé avec succès."

def get_new_achievements_for_user(user_id):
    if not isinstance(user_id, int):
        raise BadRequest("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    new_achievements = UserAchievement.query.filter_by(user_id=user_id, is_read=False, reward_claimed=True).all()
    achievement_list = []
    for user_ach in new_achievements:
        achievement = Achievement.query.get(user_ach.achievement_id)
        if not achievement:
            continue
        rewards_data = []
        for reward in achievement.rewards:
            rew_info = {
                "type": reward.type,
                "value": reward.value,
                "name": None,
                "description": None,
                "image_url": None
            }
            if reward.type == "COSMETIC" and reward.cosmetic_id:
                cosmetic = Cosmetic.query.get(reward.cosmetic_id)
                if cosmetic:
                    rew_info["name"] = cosmetic.name
                    rew_info["description"] = cosmetic.description
                    rew_info["image_url"] = cosmetic.image_url
            elif reward.type == "BADGE" and reward.badge_id:
                badge = Badge.query.get(reward.badge_id)
                if badge:
                    rew_info["name"] = badge.name
                    rew_info["description"] = badge.description
                    rew_info["image_url"] = badge.image_url
            elif reward.type in ["POINTS", "XP"]:
                rew_info["name"] = f"{reward.value} {reward.type}"
                rew_info["description"] = f"+{reward.value} points de score global" if reward.type == "POINTS" else f"+{reward.value} points d'expérience"
            rewards_data.append(rew_info)
        achievement_list.append({
            "user_achievement_id": user_ach.id,
            "achievement_id": achievement.id,
            "title": achievement.name,
            "description": achievement.description,
            "unlocked_at": user_ach.unlocked_at,
            "rewards": rewards_data
        })
    return achievement_list

def is_single_requirement_met(user_id, requirement):
    config = REQUIREMENT_CONFIG.get(requirement.type)
    if not config:
        return False
    foreign_key = config.get("foreign_key")
    target_val = getattr(requirement, foreign_key, None) if foreign_key else None
    return config["check"](user_id, requirement, target_val)

def check_category_completion(user_id, req, completed=True):
    challenges_in_category = Challenge.query.filter_by(category_id=req.category_id).all()
    if not challenges_in_category:
        return False
    completed_count = ChallengeSubmission.query.filter_by(user_id=user_id, is_correct=True).filter(ChallengeSubmission.challenge_id.in_([c.id for c in challenges_in_category])).count()
    target_count = len(challenges_in_category) if completed else req.count
    return completed_count >= target_count


def requirement_verification(user_id, action_type, target_id):
    print(f"[DEBUG] [EVALUATE] Action: {action_type} | Target: {target_id}")
    user = User.query.get(user_id)
    if not user:
        return False, []
    candidate_achievement_ids = set()
    if action_type == 'CHALLENGE_COMPLETION':
        challenge = Challenge.query.get(target_id)
        if challenge:
            reqs = AchievementRequirement.query.filter_by(type='CHALLENGE_COMPLETION', challenge_id=target_id).all()
            candidate_achievement_ids.update(r.achievement_id for r in reqs)
            total_challenges = ChallengeSubmission.query.filter_by(user_id=user_id, is_correct=True).count()
            reqs = AchievementRequirement.query.filter(AchievementRequirement.type == 'CHALLENGE_COMPLETION_COUNT', AchievementRequirement.count <= total_challenges).all()
            candidate_achievement_ids.update(r.achievement_id for r in reqs)
            reqs = AchievementRequirement.query.filter_by(type='CATEGORY_COMPLETION', category_id=challenge.category_id).all()
            candidate_achievement_ids.update(r.achievement_id for r in reqs)
            cat_challenges = ChallengeSubmission.query.join(Challenge).filter(
                ChallengeSubmission.user_id == user_id, 
                ChallengeSubmission.is_correct == True, 
                Challenge.category_id == challenge.category_id
            ).count()
            reqs = AchievementRequirement.query.filter(
                AchievementRequirement.type == 'CATEGORY_COMPLETION_COUNT', 
                AchievementRequirement.category_id == challenge.category_id, 
                AchievementRequirement.count <= cat_challenges
            ).all()
            candidate_achievement_ids.update(r.achievement_id for r in reqs)
    elif action_type == 'BADGE_EARNED':
        reqs = AchievementRequirement.query.filter_by(type='BADGE_OWNERSHIP', badge_id=target_id).all()
        candidate_achievement_ids.update(r.achievement_id for r in reqs)
        total_badges = UserBadge.query.filter_by(user_id=user_id).count()
        reqs = AchievementRequirement.query.filter(AchievementRequirement.type == 'BADGE_OWNERSHIP_COUNT', AchievementRequirement.count <= total_badges).all()
        candidate_achievement_ids.update(r.achievement_id for r in reqs)
    elif action_type == 'COSMETIC_EARNED':
        reqs = AchievementRequirement.query.filter_by(type='COSMETIC_OWNERSHIP', cosmetic_id=target_id).all()
        candidate_achievement_ids.update(r.achievement_id for r in reqs)
        total_cosmetics = UserCosmetic.query.filter_by(user_id=user_id).count()
        reqs = AchievementRequirement.query.filter(AchievementRequirement.type == 'COSMETIC_OWNERSHIP_COUNT', AchievementRequirement.count <= total_cosmetics).all()
        candidate_achievement_ids.update(r.achievement_id for r in reqs)
    elif action_type == 'POINTS_EARNED':
        reqs = AchievementRequirement.query.filter(AchievementRequirement.type == 'POINTS_EARNED', AchievementRequirement.count <= user.global_score).all()
        candidate_achievement_ids.update(r.achievement_id for r in reqs)
    elif action_type == 'LEVEL_REACHED':
        reqs = AchievementRequirement.query.filter(AchievementRequirement.type == 'LEVEL_REACHED', AchievementRequirement.count <= user.level).all()
        candidate_achievement_ids.update(r.achievement_id for r in reqs)
    elif action_type == 'CONNECTION_STREAK':
        reqs = AchievementRequirement.query.filter(AchievementRequirement.type == 'CONNECTION_STREAK', AchievementRequirement.count <= user.connection_streak).all()
        candidate_achievement_ids.update(r.achievement_id for r in reqs)
    elif action_type == 'CONNECTION_DATE':
        if user.last_connection:
            reqs = AchievementRequirement.query.filter_by(type='CONNECTION_DATE').all()
            for r in reqs:
                if r.target_date and r.target_date.date() == user.last_connection.date():
                    candidate_achievement_ids.add(r.achievement_id)
    if not candidate_achievement_ids:
        return False, []
    validated_achievement_ids = []
    for ach_id in candidate_achievement_ids:
        achievement = Achievement.query.get(ach_id)
        if not achievement:
            continue
        already_unlocked = UserAchievement.query.filter_by(user_id=user_id, achievement_id=ach_id).first()
        if already_unlocked:
            continue
        all_passed = all(is_single_requirement_met(user_id, req) for req in achievement.requirements)
        if all_passed:
            validated_achievement_ids.append(ach_id)
    return bool(validated_achievement_ids), validated_achievement_ids

def reward_dispatch(user_id, list):
    print("[DEBUG] ------------------------------------------------------------------------------ [REWARD DISPATCH]")
    new_user_achievements = []
    existing_achievements = UserAchievement.query.filter_by(user_id=user_id).with_entities(UserAchievement.achievement_id).all()
    existing_achievement_ids = {ach.achievement_id for ach in existing_achievements}
    for achievement_id in list:
        if achievement_id in existing_achievement_ids:
            continue
        new_user_achievement = UserAchievement()
        new_user_achievement.user_id = user_id
        new_user_achievement.achievement_id = achievement_id
        new_user_achievement.unlocked_at = datetime.now()
        db.session.add(new_user_achievement)
        new_user_achievements.append(new_user_achievement)
    db.session.commit()
    return [ua.id for ua in new_user_achievements]

def process_achievement_reward(list):
    print("[DEBUG] ------------------------------------------------------------------------------ [PROCESS REWARDS]")
    for user_achievement_id in list:
        user_achievement = UserAchievement.query.get(user_achievement_id)
        if not user_achievement or user_achievement.reward_claimed:
            continue
        achievement = Achievement.query.get(user_achievement.achievement_id)
        if not achievement:
            continue
        for reward in achievement.rewards:
            if reward.type == "COSMETIC":
                user_cosmetic = UserCosmetic.query.filter_by(user_id=user_achievement.user_id, cosmetic_id=reward.cosmetic_id).first()
                if not user_cosmetic:
                    new_user_cosmetic = UserCosmetic(user_id=user_achievement.user_id, cosmetic_id=reward.cosmetic_id)
                    db.session.add(new_user_cosmetic)
            elif reward.type == "BADGE":
                user_badge = UserBadge.query.filter_by(user_id=user_achievement.user_id, badge_id=reward.badge_id).first()
                if not user_badge:
                    new_user_badge = UserBadge(user_id=user_achievement.user_id, badge_id=reward.badge_id)
                    db.session.add(new_user_badge)
            elif reward.type == "POINTS":
                user = User.query.get(user_achievement.user_id)
                if user: user.global_score += reward.value
            elif reward.type == "XP":
                user = User.query.get(user_achievement.user_id)
                if user: user.xp += reward.value
        user_achievement.reward_claimed = True
    db.session.commit()

def evaluate_achievements_for_user(user_id, action_type=None, target_id=None):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = User.query.filter_by(id=user_id).with_entities(User.id).first()
    if not user:
        raise InternalServerError("USER_NOT_FOUND|Utilisateur non trouvé.")
    if action_type and not AUTHORIZED_ACTION_TYPES.get(action_type):
        raise InternalServerError(f"INVALID_ACTION_TYPE|Type d'action invalide: {action_type}")
    has_rewards, ach_list = requirement_verification(user_id, action_type, target_id)
    if has_rewards:
        process_achievement_reward(list=reward_dispatch(user_id, ach_list))