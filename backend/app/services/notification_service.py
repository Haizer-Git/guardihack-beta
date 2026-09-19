from datetime import datetime, timedelta

from extensions import db
from sqlalchemy import func, not_
from werkzeug.exceptions import InternalServerError, NotFound, BadRequest
from models.core import (
    Notification, GlobalNotification, GlobalNotificationRead,
    User
)

def send_notification(user_id, title, message):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|L'utilisateur spécifié n'existe pas.")
    new_notification = Notification()
    new_notification.user_id = user_id
    new_notification.title = title
    new_notification.message = message
    db.session.add(new_notification)
    db.session.commit()
    return f"Notification envoyée avec succès à {user.username}."

def send_global_notification(title, message, debut=None, end=None):
    if isinstance(debut, str):
        debut = datetime.strptime(debut, '%Y-%m-%d %H:%M:%S')
    if isinstance(end, str):
        end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    if debut is None:
        debut = datetime.now()
    if debut < datetime.now() - timedelta(minutes=2):
        raise BadRequest("INVALID_DEBUT|La date de début ne peut pas être dans le passé.")
    if end is not None and end <= debut:
        raise BadRequest("INVALID_END|La date de fin doit être après la date de début.")
    new_global_notification = GlobalNotification()
    new_global_notification.title = title
    new_global_notification.message = message
    new_global_notification.debut = debut
    new_global_notification.end = end
    db.session.add(new_global_notification)
    db.session.commit()

    return "Notification globale envoyée avec succès."

def read_notification(user_id, notification_id):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    if not isinstance(notification_id, int):
        raise BadRequest("INVALID_NOTIFICATION_ID|L'ID de la notification doit être un entier.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|L'utilisateur spécifié n'existe pas.")
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if not notification:
        raise NotFound("NOTIFICATION_NOT_FOUND|La notification spécifiée n'existe pas pour cet utilisateur.")
    notification.is_read = True
    db.session.commit()

def unread_notification(user_id, notification_id):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    if not isinstance(notification_id, int):
        raise BadRequest("INVALID_NOTIFICATION_ID|L'ID de la notification doit être un entier.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|L'utilisateur spécifié n'existe pas.")
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if not notification:
        raise NotFound("NOTIFICATION_NOT_FOUND|La notification spécifiée n'existe pas pour cet utilisateur.")
    notification.is_read = False
    db.session.commit()

def read_global_notification(user_id, global_notification_id):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    if not isinstance(global_notification_id, int):
        raise BadRequest("INVALID_GLOBAL_NOTIFICATION_ID|L'ID de la notification globale doit être un entier.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|L'utilisateur spécifié n'existe pas.")
    global_notification = GlobalNotification.query.filter_by(id=global_notification_id).first()
    if not global_notification:
        raise NotFound("GLOBAL_NOTIFICATION_NOT_FOUND|La notification globale spécifiée n'existe pas.")
    if global_notification.debut > datetime.now() or (global_notification.end and global_notification.end < datetime.now()):
        raise BadRequest("GLOBAL_NOTIFICATION_ERROR|Erreur lors de la lecture de la notification globale.")
    existing_read = GlobalNotificationRead.query.filter_by(user_id=user_id, notification_id=global_notification_id).first()
    if existing_read:
        return
    new_read = GlobalNotificationRead()
    new_read.user_id = user_id
    new_read.notification_id = global_notification_id
    db.session.add(new_read)
    db.session.commit()

def unread_global_notification(user_id, global_notification_id):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    if not isinstance(global_notification_id, int):
        raise BadRequest("INVALID_GLOBAL_NOTIFICATION_ID|L'ID de la notification globale doit être un entier.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|L'utilisateur spécifié n'existe pas.")
    global_notification = GlobalNotification.query.filter_by(id=global_notification_id).first()
    if not global_notification:
        raise NotFound("GLOBAL_NOTIFICATION_NOT_FOUND|La notification globale spécifiée n'existe pas.")
    existing_read = GlobalNotificationRead.query.filter_by(user_id=user_id, notification_id=global_notification_id).first()
    if existing_read:
        db.session.delete(existing_read)
        db.session.commit()

def list_global_notifications():
    total_users = User.query.count()
    global_notifications = GlobalNotification.query.all()
    read_counts_query = db.session.query(
        GlobalNotificationRead.notification_id, 
        func.count(GlobalNotificationRead.user_id)
    ).group_by(GlobalNotificationRead.notification_id).all()
    read_counts_map = {notif_id: count for notif_id, count in read_counts_query}
    notifications = []
    for notification in global_notifications:
        read_count = read_counts_map.get(notification.id, 0)
        read_percentage = round((read_count / total_users * 100), 1) if total_users > 0 else 0.0
        notifications.append({
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "read_count": read_count,
            "total_users": total_users,
            "read_percentage": read_percentage,
            "created_at": notification.created_at.strftime("%d/%m/%Y %H:%M:%S"),
            "debut": notification.debut.strftime("%d/%m/%Y %H:%M:%S"),
            "end": notification.end.strftime("%d/%m/%Y %H:%M:%S") if notification.end else None
        })
    return notifications

def count_notification(user_id):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|L'utilisateur spécifié n'existe pas.")
    return user.unread_notifications_count

def get_new_notifications(user_id):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|L'utilisateur spécifié n'existe pas.")
    personal_unread = Notification.query.filter_by(user_id=user_id, is_read=False).all()
    read_globals_subquery = db.session.query(GlobalNotificationRead.notification_id).filter_by(user_id=user_id)
    global_unread = GlobalNotification.query.filter(not_(GlobalNotification.id.in_(read_globals_subquery))).filter(GlobalNotification.debut <= datetime.now()).filter(
        (GlobalNotification.end == None) | (GlobalNotification.end >= datetime.now())).all()
    notifications = []
    for notification in personal_unread:
        notifications.append({
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "is_read": notification.is_read,
            "type": "personal",
            "created_at": notification.created_at.strftime("%d/%m/%Y %H:%M:%S")
        })
    for notification in global_unread:
        notifications.append({
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "is_read": False,
            "type": "global",
            "created_at": notification.created_at.strftime("%d/%m/%Y %H:%M:%S")
        })
    notifications.sort(key=lambda x: x["created_at"], reverse=True)
    return notifications, user.unread_notifications_count

def get_all_notifications(user_id):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|L'utilisateur spécifié n'existe pas.")
    personal_notifications = Notification.query.filter_by(user_id=user_id).all()
    global_notifications = GlobalNotification.query.filter(GlobalNotification.debut <= datetime.now()).filter(
        (GlobalNotification.end == None) | (GlobalNotification.end >= datetime.now())).all()
    read_global_ids = {
        read.notification_id 
        for read in GlobalNotificationRead.query.filter_by(user_id=user_id).all()
    }
    notifications = []
    for notification in personal_notifications:
        notifications.append({
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "is_read": notification.is_read,
            "type": "personal",
            "created_at": notification.created_at.strftime("%d/%m/%Y %H:%M:%S")
        })
    for notification in global_notifications:
        notifications.append({
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "is_read": notification.id in read_global_ids,
            "type": "global",
            "created_at": notification.created_at.strftime("%d/%m/%Y %H:%M:%S")
        })
    notifications.sort(key=lambda x: x["created_at"], reverse=True)
    return notifications