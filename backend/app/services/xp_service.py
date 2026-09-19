from werkzeug.exceptions import InternalServerError, NotFound, BadRequest

from extensions import db
from models.core import (
    User
)
from models.core.challenge import (
    Challenge
)
import math

AUTHORIZED_DIFFICULTIES = {
    "INTRO": 0.25,
    "EASY": 0.5,
    "MEDIUM": 1,
    "HARD": 1.5,
    "EXPERT": 2
}


def adjust_xp(user_id, xp_change, challenge_difficulty=None, manual=None):
    if not isinstance(user_id, int):
        raise BadRequest("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    if not isinstance(xp_change, (int, float)):
        raise BadRequest("INVALID_XP_CHANGE|Le changement d'XP doit être un nombre.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|L'utilisateur spécifié n'existe pas.")
    xp_change *= AUTHORIZED_DIFFICULTIES.get(challenge_difficulty, 2)
    user.xp = max(0, user.xp + xp_change)
    db.session.commit()
    if manual:
        return f"XP ajusté manuellement de {xp_change} points avec succès."
    return xp_change

def daily_xp_bonus(user_id, streak):
    bonus = 10 * math.sqrt(streak)
    if adjust_xp(user_id=user_id, xp_change=bonus):
        return bonus
    return 0
