import threading
from flask import current_app
from sqlalchemy import event, inspect
from extensions import db
from services.achievement_service import evaluate_achievements_for_user
from models.core import (
    UserBadge, UserCosmetic, User,
    UserAchievement,
)
from models.core.challenge import (
    ChallengeSubmission
)

def trigger_achievement_dispatch(user_id, action_type=None, target_id=None):
    if not user_id:
        return
    if 'pending_achievements' not in db.session.info:
        db.session.info['pending_achievements'] = []
        
    db.session.info['pending_achievements'].append({
        'user_id': user_id,
        'action_type': action_type,
        'target_id': target_id
    })

@event.listens_for(db.session, 'after_commit')
def process_deferred_achievements(session):
    events = session.info.pop('pending_achievements', [])
    if not events:
        return
    try:
        app = current_app._get_current_object()
    except RuntimeError:
        for ev in events:
            try:
                evaluate_achievements_for_user(ev['user_id'], ev['action_type'], ev['target_id'])
            except Exception as e:
                print(f"Erreur d'évaluation des succès (CLI) : {e}")
        return
    def run_evals(app_context, evs):
        with app_context:
            for ev in evs:
                try:
                    evaluate_achievements_for_user(ev['user_id'], ev['action_type'], ev['target_id'])
                except Exception as e:
                    print(f"Erreur lors de l'évaluation des succès (Thread) : {e}")

    threading.Thread(target=run_evals, args=(app.app_context(), events)).start()

# ─────────────────────────────────────────────────────────────────────────────
# LISTENERS
# ─────────────────────────────────────────────────────────────────────────────

@event.listens_for(ChallengeSubmission, 'after_insert')
def watcher_trigger_challenge(mapper, connection, target):
    if target.is_correct:
        trigger_achievement_dispatch(target.user_id, 'CHALLENGE_COMPLETION', target.challenge_id)

@event.listens_for(UserBadge, 'after_insert')
def watcher_trigger_badge(mapper, connection, target):
    trigger_achievement_dispatch(target.user_id, 'BADGE_EARNED', target.badge_id)

@event.listens_for(UserCosmetic, 'after_insert')
def watcher_trigger_cosmetic(mapper, connection, target):
    trigger_achievement_dispatch(target.user_id, 'COSMETIC_EARNED', target.cosmetic_id)

@event.listens_for(UserAchievement, 'after_insert')
def watcher_trigger_achievement(mapper, connection, target):
    trigger_achievement_dispatch(target.user_id, 'ACHIEVEMENT_UNLOCKED', target.achievement_id)

@event.listens_for(User, 'after_update')
def watcher_trigger_user(mapper, connection, target):
    state = inspect(target)
    if state.attrs.global_score.history.has_changes():
        trigger_achievement_dispatch(target.id, 'POINTS_EARNED', target.global_score)
    if state.attrs.xp.history.has_changes():
        trigger_achievement_dispatch(target.id, 'LEVEL_REACHED', target.xp)
    if state.attrs.connection_streak.history.has_changes():
        trigger_achievement_dispatch(target.id, 'CONNECTION_STREAK', target.connection_streak)
    if state.attrs.last_connection.history.has_changes():
        trigger_achievement_dispatch(target.id, 'CONNECTION_DATE', target.last_connection)