from sqlalchemy import func
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import NotFound, BadRequest
from datetime import datetime
from extensions import db
from models.core import (
    User, ScoreHistory, UserProfile
)
from services.notification_service import (
    send_notification
)

def adjust_score(user_id, score_change, admin_id=None, history=False, reason=None, manual=False):
    if not isinstance(user_id, int):
        raise BadRequest("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    if not isinstance(score_change, int):
        raise BadRequest("INVALID_SCORE_CHANGE|Le changement de score doit être un entier.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    if history and not reason:
        raise BadRequest("MISSING_REASON|Une raison explicite doit être fournie si le score est visible dans l'historique du joueur.")
    user.global_score = max(0, user.global_score + score_change)
    score_entry = ScoreHistory()
    score_entry.user_id = user_id
    score_entry.change = score_change
    score_entry.reason = reason if reason else "Ajustement système/admin silencieux"
    score_entry.score_total = user.global_score
    score_entry.timestamp = datetime.now()
    score_entry.history = history
    score_entry.manual = manual
    if manual and admin_id:
        score_entry.manual_user_id = admin_id
    db.session.add(score_entry)
    db.session.commit()
    if manual:
        return f"Score ajusté manuellement de {score_change} points avec succès."
    return user.global_score

def get_score_history(target_username):
    user = User.query.filter_by(username=target_username).with_entities(User.id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    history = ScoreHistory.query.filter_by(user_id=user.id, history=True).order_by(ScoreHistory.timestamp.desc()).all()
    result = []
    for entry in history:
        result.append({
            "timestamp": entry.timestamp.strftime("%d/%m/%Y %H:%M:%S"),
            "change": entry.change,
            "reason": entry.reason,
            "score_total": entry.score_total
        })
    return result

def get_admin_score_history(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    history = ScoreHistory.query.filter_by(user_id=user.id).order_by(ScoreHistory.timestamp.desc()).all()
    result = []
    for entry in history:
        result.append({
            "timestamp": entry.timestamp.strftime("%d/%m/%Y %H:%M:%S"),
            "change": entry.change,
            "reason": entry.reason,
            "score_total": entry.score_total,
            "is_public": entry.history,
            "is_manual": entry.manual,
            "admin_id": entry.manual_user_id if entry.manual_user_id else None
        })
    return result

def get_recent_activity(target_username=None, limit=3):
    user = User.query.filter_by(username=target_username).with_entities(User.id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    history = ScoreHistory.query.filter_by(user_id=user.id, history=True).order_by(ScoreHistory.timestamp.desc()).limit(limit).all()
    result = []
    for entry in history:
        result.append({
            "timestamp": entry.timestamp.strftime("%d/%m/%Y %H:%M:%S"),
            "change": entry.change,
            "reason": entry.reason,
            "score_total": entry.score_total
        })
    return result

def get_leaderboard(offset, limit=15):
    if not isinstance(offset, int) or offset < 0:
        offset = 0
    min_score = 0
    total_users = db.session.query(func.count(User.id)).filter(User.global_score > min_score).scalar()
    top_users = (User.query.order_by(User.global_score.desc()).filter(User.global_score > min_score).options(joinedload(User.profile)).limit(limit).offset(offset).all())
    leaderboard = []
    for user in top_users:
        leaderboard.append({
            "rank": user.rank,
            "username": user.username,
            "avatar": user.profile.avatar_cosmetic.icon.filepath if user.profile.avatar_cosmetic else None,
            "global_score": user.global_score,
            "affiliation": user.profile.affiliation
        })
    return total_users, leaderboard

def check_overtake(user_id, old_score, new_score):
    if not isinstance(user_id, int):
        raise BadRequest("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    current_user = User.query.filter_by(id=user_id).first()
    if not current_user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    if old_score >= new_score:
        return []
    overtaken_users = (User.query.filter(User.global_score >= old_score, User.global_score <= new_score).filter(User.id != user_id).all())
    notified_users = []
    for opponent in overtaken_users:
        new_rank = opponent.rank  
        send_notification(user_id=opponent.id, type="OVERTAKEN", data={"username": current_user.username, "new_rank": new_rank})
        notified_users.append(opponent.id)
    return notified_users