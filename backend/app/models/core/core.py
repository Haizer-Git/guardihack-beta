from sqlalchemy import func, and_, not_
from sqlalchemy.ext.hybrid import hybrid_property
from extensions import db
import math, os
from datetime import datetime

coeff = float(os.getenv('XP_COEFFICIENT', "1.0"))

class User(db.Model):
    __tablename__ = 'users'
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    username = db.Column(db.String(32), unique=True, nullable=False)
    passphrase_hash = db.Column(db.String(255), nullable=False)
    mail = db.Column(db.String(255), unique=True, nullable=False)
    type = db.Column(db.String(255), default='USER', nullable=False)
    global_score = db.Column(db.Integer, default=0, nullable=False, index=True)
    xp = db.Column(db.Integer, default=0, nullable=False)
    guardicoin = db.Column(db.Integer, default=0, nullable=False)
    last_connection = db.Column(db.DateTime, nullable=True)
    connection_streak = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    status = db.Column(db.String(32), default='PENDING', nullable=False)
    secret_key = db.Column(db.String(255), nullable=False)
    # -- Clés étrangères --
    preset_id = db.Column(db.Integer, db.ForeignKey('user_presets.id', use_alter=True, name='fk_user_preset'), nullable=False)
    # -- Relations --
    profile = db.relationship('UserProfile', back_populates='user', uselist=False, lazy=True)
    badges = db.relationship('Badge', secondary='user_badges', back_populates='users', lazy=True)
    badge_pivots = db.relationship('UserBadge', back_populates='user', lazy=True, overlaps="badges")
    score_history = db.relationship('ScoreHistory', foreign_keys='ScoreHistory.user_id', back_populates='user')
    manual_score_history = db.relationship('ScoreHistory', foreign_keys='ScoreHistory.manual_user_id', back_populates='manual_user')
    submissions = db.relationship('ChallengeSubmission', back_populates='user', order_by='ChallengeSubmission.submitted_at.desc()', lazy=True)
    inventory = db.relationship('UserCosmetic', back_populates='user', lazy=True)
    user_preset = db.relationship('UserPreset', back_populates='users', foreign_keys=[preset_id], lazy=True)
    created_presets = db.relationship('UserPreset', back_populates='creator', foreign_keys='[UserPreset.created_by]', lazy=True)
    created_badges = db.relationship('Badge', back_populates='creator', lazy=True)
    created_cosmetics = db.relationship('Cosmetic', back_populates='creator', lazy=True)
    created_tokens = db.relationship('PresetToken', back_populates='creator', lazy=True)
    created_challenges = db.relationship('Challenge', back_populates='creator', lazy=True)
    notifications = db.relationship('Notification', back_populates='user', lazy=True)
    instances = db.relationship('UserInstance', back_populates='user', lazy=True)
    global_notification_reads = db.relationship('GlobalNotificationRead', back_populates='user', lazy=True)
    achievements = db.relationship('UserAchievement', back_populates='user', lazy=True)
    status_history = db.relationship('UserStatusHistory', foreign_keys='UserStatusHistory.user_id', back_populates='user', lazy=True)
    admin_status_history = db.relationship('UserStatusHistory', foreign_keys='UserStatusHistory.admin_id', back_populates='admin', lazy=True)
    # -- Propriétés --
    @property
    def challenges_count(self):
        submission = self.submissions
        unique_challenges = {sub.challenge_id for sub in submission}
        validated_challenges = {sub.challenge_id for sub in submission if sub.is_correct == True}
        return {
            "total" : len(submission),
            "unique" : len(unique_challenges),
            "validated" : len(validated_challenges)
        }
    @property
    def achievements_count(self):
        return len(self.achievements)
    @property
    def inventory_count(self):
        return len(self.inventory)
    @property
    def active_status_info(self):
        active_status = next((status for status in self.status_history if status.ended_at is None or status.ended_at > datetime.now()), None)
        if active_status:
            return {
                "status": active_status.status,
                "reason": active_status.reason,
                "changed_at": active_status.changed_at,
                "ended_at": active_status.ended_at if active_status.ended_at else None
            }
    @property
    def rank(self):
        higher_scores_count = db.session.query(func.count(User.id)).filter(User.global_score > self.global_score).scalar()
        return higher_scores_count + 1
    @property
    def level(self):
        if self.xp <= 0:
            return 1
        return math.floor(coeff * math.sqrt(self.xp)) + 1
    @property
    def next_level_xp(self):
        current_level = self.level
        xp_start = math.ceil(((current_level - 1) / coeff) ** 2)
        xp_target = math.ceil((current_level / coeff) ** 2)
        return xp_start, xp_target
    @property
    def active_instance(self):
        return self.instances[0] if self.instances else None
    @property
    def unread_notifications_count(self):
        personal_unread = sum(1 for notif in self.notifications if not notif.is_read)
        read_globals_ids = {r.notification_id for r in self.global_notification_reads}
        now = datetime.now()
        global_query = GlobalNotification.query.filter(
            GlobalNotification.debut <= now,
            (GlobalNotification.end == None) | (GlobalNotification.end >= now)
        )
        if read_globals_ids:
            global_query = global_query.filter(not_(GlobalNotification.id.in_(read_globals_ids)))
        global_unread_count = global_query.count()
        return personal_unread + global_unread_count

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    affiliation = db.Column(db.String(64), nullable=False)
    niveau = db.Column(db.String(64), nullable=True)
    classe = db.Column(db.String(64), nullable=True)
    is_private = db.Column(db.Boolean, default=True, nullable=False)
    # -- Clés étrangères --
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    avatar_id = db.Column(db.Integer, db.ForeignKey('cosmetics.id'), default=None, nullable=True)
    banner_id = db.Column(db.Integer, db.ForeignKey('cosmetics.id'), default=None, nullable=True)
    # -- Relations --
    user = db.relationship('User', back_populates='profile', lazy=True)
    avatar_cosmetic = db.relationship('Cosmetic', foreign_keys=[avatar_id], back_populates='avatar_profiles', lazy=True)
    banner_cosmetic = db.relationship('Cosmetic', foreign_keys=[banner_id], back_populates='banner_profiles', lazy=True)

class UserPreset(db.Model):
    __tablename__ = 'user_presets'
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), default='USER', nullable=False)
    affiliation = db.Column(db.String(64), nullable=False)
    # -- Clés étrangères --
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # -- Relations --
    creator = db.relationship('User', back_populates='created_presets', foreign_keys=[created_by], lazy=True)
    users = db.relationship('User', back_populates='user_preset', foreign_keys='[User.preset_id]', lazy=True)
    tokens = db.relationship('PresetToken', back_populates='preset', lazy=True)
    # -- Propriétés -- 
    @property
    def token_count(self):
        return len(self.tokens)

class PresetToken(db.Model):
    __tablename__ = 'preset_tokens'
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    token = db.Column(db.String(255), unique=True, nullable=False)
    uses = db.Column(db.Integer, default=0, nullable=False)
    max_uses = db.Column(db.Integer, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    mail = db.Column(db.String(255), nullable=True)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    niveau = db.Column(db.String(64), nullable=True)
    classe = db.Column(db.String(64), nullable=True)
    auto = db.Column(db.Boolean, default=False, nullable=False)
    # -- Clés étrangères --
    preset_id = db.Column(db.Integer, db.ForeignKey('user_presets.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # -- Relations --
    preset = db.relationship('UserPreset', back_populates='tokens', lazy=True)
    creator = db.relationship('User', back_populates='created_tokens', lazy=True)
    # -- Propriétés --
    @property
    def is_active(self):
        if self.expires_at is not None and self.expires_at < datetime.now():
            return "EXPIRED"
        elif self.uses >= self.max_uses:
            return "MAX_USES_REACHED"
        return "ACTIVE"

class Icon(db.Model):
    __tablename__ = "icons"
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    filetype = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    # -- Relations --
    badges = db.relationship('Badge', back_populates='icon', lazy=True)
    cosmetics = db.relationship('Cosmetic', back_populates='icon', lazy=True)

class Badge(db.Model):
    __tablename__ = "badges"
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    type = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    # -- Clés étrangères --
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    icon_id = db.Column(db.Integer, db.ForeignKey('icons.id'), nullable=True)
    # -- Relations --
    users = db.relationship('User', secondary='user_badges', back_populates='badges')
    creator = db.relationship('User', back_populates='created_badges', lazy=True)
    badge_pivots = db.relationship('UserBadge', back_populates='badge', lazy=True)
    requirements = db.relationship('AchievementRequirement', back_populates='badge', lazy=True)
    icon = db.relationship('Icon', back_populates='badges', lazy=True)
    rewards = db.relationship('AchievementReward', back_populates='badge', lazy=True)
    # -- Propriétés --
    @property
    def user_count(self):
        return len(self.users)

class UserBadge(db.Model):
    __tablename__ = "user_badges"
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    earned_at = db.Column(db.DateTime, default=datetime.now, onupdate=db.func.now(), nullable=True)
    # -- Clés étrangères --
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    # -- Relations --
    user = db.relationship('User', back_populates='badge_pivots', lazy=True)
    badge = db.relationship('Badge', back_populates='badge_pivots', lazy=True)
    # -- Contraintes --
    __table_args__ = (db.UniqueConstraint('user_id', 'badge_id', name='_user_badge_uc'),)

class Cosmetic(db.Model):
    __tablename__ = "cosmetics"
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    type = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    rarete = db.Column(db.String(32), nullable=False)
    exclu = db.Column(db.Boolean, default=False, nullable=False)
    global_cosmetic = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    # -- Clés étrangères --
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    icon_id = db.Column(db.Integer, db.ForeignKey('icons.id'), nullable=True)
    # -- Relations --
    inventory_entries = db.relationship('UserCosmetic', back_populates='cosmetic', lazy=True)
    creator = db.relationship('User', back_populates='created_cosmetics', lazy=True)
    avatar_profiles = db.relationship('UserProfile', foreign_keys='[UserProfile.avatar_id]', back_populates='avatar_cosmetic')
    banner_profiles = db.relationship('UserProfile', foreign_keys='[UserProfile.banner_id]', back_populates='banner_cosmetic')
    requirements = db.relationship('AchievementRequirement', back_populates='cosmetic', lazy=True)
    icon = db.relationship('Icon', back_populates='cosmetics', lazy=True)
    rewards = db.relationship('AchievementReward', back_populates='cosmetic', lazy=True)
    # -- Propriétés --
    @property
    def user_count(self):
        return len(self.inventory_entries)
    @property
    def active_user(self):
        if self.type == "AVATAR":
            return len(self.avatar_profiles)
        elif self.type == "BANNER":
            return len(self.banner_profiles)

class UserCosmetic(db.Model):
    __tablename__ = "user_cosmetics"
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    earned_at = db.Column(db.DateTime, default=datetime.now, nullable=True)
    # -- Clés étrangères --
    cosmetic_id = db.Column(db.Integer, db.ForeignKey('cosmetics.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # -- Relations --
    user = db.relationship('User', back_populates='inventory', lazy=True)
    cosmetic = db.relationship('Cosmetic', back_populates='inventory_entries', lazy=True)
    # -- Contraintes --
    __table_args__ = (db.UniqueConstraint('user_id', 'cosmetic_id', name='unique_user_cosmetic'),)

class Achievement(db.Model):
    __tablename__ = "achievements"
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    # -- Clés étrangères --
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # -- Relations --
    users = db.relationship('UserAchievement', back_populates='achievement', lazy=True)
    requirements = db.relationship('AchievementRequirement', back_populates='achievement', lazy=True)
    rewards = db.relationship('AchievementReward', back_populates='achievement', lazy=True)
    # -- Propriétés --
    @property
    def requirement_count(self):
        return len(self.requirements)
    @property
    def reward_count(self):
        return len(self.rewards)
    @property
    def unlocked_count(self):
        return len(self.users)
    @property
    def requirement_ids(self):
        return [req.id for req in self.requirements]
    @property
    def requirement_types(self):
        return [req.type for req in self.requirements]

class AchievementRequirement(db.Model):
    __tablename__ = "achievement_requirements"
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    type = db.Column(db.String(32), nullable=False)
    count = db.Column(db.Integer, nullable=True)
    target_date = db.Column(db.DateTime, nullable=True)
    # -- Clés étrangères --
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=True)
    cosmetic_id = db.Column(db.Integer, db.ForeignKey('cosmetics.id'), nullable=True)
    # -- Relations --
    achievement = db.relationship('Achievement', back_populates='requirements', lazy=True)
    challenge = db.relationship('Challenge', back_populates='requirements', lazy=True)
    category = db.relationship('Category', back_populates='requirements', lazy=True)
    badge = db.relationship('Badge', back_populates='requirements', lazy=True)
    cosmetic = db.relationship('Cosmetic', back_populates='requirements', lazy=True)

class AchievementReward(db.Model):
    __tablename__ = "achievement_rewards"
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    type = db.Column(db.String(32), nullable=False)
    value = db.Column(db.Integer, nullable=True)
    # -- Clés étrangères --
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    cosmetic_id = db.Column(db.Integer, db.ForeignKey('cosmetics.id'), nullable=True)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=True)
    # -- Relations --
    achievement = db.relationship('Achievement', back_populates='rewards', lazy=True)
    cosmetic = db.relationship('Cosmetic', back_populates='rewards', lazy=True)
    badge = db.relationship('Badge', back_populates='rewards', lazy=True)

class UserAchievement(db.Model):
    __tablename__ = "user_achievements"
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    reward_claimed = db.Column(db.Boolean, default=False, nullable=False)
    # -- Relations --
    user = db.relationship('User', back_populates='achievements', lazy=True)
    achievement = db.relationship('Achievement', back_populates='users', lazy=True)
    # -- Contraintes --
    __table_args__ = (db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),)

class ScoreHistory(db.Model):
    __tablename__ = "score_history"
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    change = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    score_total = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)
    history = db.Column(db.Boolean, default=False, nullable=False)
    manual = db.Column(db.Boolean, default=False, nullable=True)
    # -- Clés étrangères --
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manual_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    # -- Relations --
    user = db.relationship('User', foreign_keys=[user_id], back_populates='score_history')
    manual_user = db.relationship('User', foreign_keys=[manual_user_id], back_populates='manual_score_history')

class Notification(db.Model):
    __tablename__ = "notifications"
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    # -- Relations --
    user = db.relationship('User', back_populates='notifications', lazy=True)

class GlobalNotification(db.Model):
    __tablename__ = "global_notifications"
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    debut = db.Column(db.DateTime, default=datetime.now, nullable=False)
    end = db.Column(db.DateTime, nullable=True)
    # -- Relations --
    reads = db.relationship('GlobalNotificationRead', back_populates='global_notification', lazy=True)

class GlobalNotificationRead(db.Model):
    __tablename__ = "global_notification_reads"
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    read_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    # -- Clés étrangères --
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notification_id = db.Column(db.Integer, db.ForeignKey('global_notifications.id'), nullable=False)
    # -- Contraintes --
    __table_args__ = (db.UniqueConstraint('user_id', 'notification_id', name='unique_user_global_notification'),)
    # -- Relations --
    user = db.relationship('User', back_populates='global_notification_reads', lazy=True)
    global_notification = db.relationship('GlobalNotification', back_populates='reads', lazy=True)

class UserStatusHistory(db.Model):
    __tablename__ = "user_status_history"
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    status = db.Column(db.String(32), nullable=False)
    old_status = db.Column(db.String(32), nullable=True)
    reason = db.Column(db.String(255), nullable=True)
    changed_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    ended_at = db.Column(db.DateTime, nullable=True)
    auto = db.Column(db.Boolean, default=False, nullable=False)
    # -- Clés étrangères --
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    # -- Relations --
    user = db.relationship('User', foreign_keys=[user_id], back_populates='status_history', lazy=True)
    admin = db.relationship('User', foreign_keys=[admin_id], back_populates='admin_status_history', lazy=True)
