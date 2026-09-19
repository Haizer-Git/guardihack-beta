from extensions import db
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'categories'
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    # -- Relations --
    challenges = db.relationship('Challenge', back_populates='category', lazy=True)
    requirements = db.relationship('AchievementRequirement', back_populates='category', lazy=True)

class Challenge(db.Model):
    __tablename__ = 'challenges'
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    name = db.Column(db.String(255), unique=True, nullable=False)
    type = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False)
    difficulty = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    secret_key = db.Column(db.String(255), nullable=False)
    flag_type = db.Column(db.String(255), nullable=False)
    master_flag = db.Column(db.String(255), nullable=False)
    encrypted_flag = db.Column(db.String(255), nullable=False)
    external_url = db.Column(db.String(255), nullable=True)
    hidden = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    # -- Clés étrangères -- 
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    docker_image_id = db.Column(db.Integer, db.ForeignKey('docker_images.id'), nullable=True)
    geoint_config_id = db.Column(db.Integer, db.ForeignKey('geoint_configs.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # -- Relations --
    category = db.relationship('Category', back_populates='challenges', lazy=True)
    docker_image = db.relationship('DockerImage', back_populates='challenges', lazy=True)
    geoint_config = db.relationship('GeointConfig', backref='challenge', lazy=True, uselist=False)
    submissions = db.relationship('ChallengeSubmission', back_populates='challenge', order_by='ChallengeSubmission.submitted_at.desc()', lazy=True)
    rotations = db.relationship('ChallengeRotation', back_populates='challenge', lazy=True)
    creator = db.relationship('User', back_populates='created_challenges', lazy=True)
    files = db.relationship('ChallengeFiles', back_populates='challenge', lazy=True)
    instances = db.relationship('UserInstance', back_populates='challenge', lazy=True)
    requirements = db.relationship('AchievementRequirement', back_populates='challenge', lazy=True)
    # -- Propriétés --
    @hybrid_property
    def is_active(self):
        if self.hidden:
            return False
        if self.type and self.type.upper() == 'PERMANENT':
            return True
        if self.type and self.type.upper() == 'ROTATION':
            return any(rotation.rotation.is_active for rotation in self.rotations)
        return False
    @is_active.expression
    def is_active(cls):
        now = datetime.now()
        active_rotations_subquery = (
            db.session.query(ChallengeRotation.challenge_id)
            .join(Rotation, ChallengeRotation.rotation_id == Rotation.id)
            .filter(Rotation.start_time <= now, Rotation.end_time >= now)
            .subquery()
        )
        return db.case(
            (cls.hidden == True, False),
            (cls.type.ilike('PERMANENT'), True),
            (cls.type.ilike('ROTATION'), cls.id.in_(active_rotations_subquery)),
            else_=False
        )

class GeointConfig(db.Model):
    __tablename__ = 'geoint_configs'
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    name = db.Column(db.String(255), unique=True, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    tolerance_radius = db.Column(db.Float, nullable=False)
    # -- Relations --
    challenges = db.relationship('Challenge', back_populates='geoint_config', lazy=True)

class ChallengeSubmission(db.Model):
    __tablename__ = 'challenge_submissions'
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    flag_submitted = db.Column(db.String(255), nullable=True)
    flag_type = db.Column(db.String(255), nullable=True)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    # -- Clés étrangères --
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    # -- Relations --
    user = db.relationship('User', back_populates='submissions', lazy=True)
    challenge = db.relationship('Challenge', back_populates='submissions', lazy=True)

class ChallengeRotation(db.Model):
    __tablename__ = 'challenge_rotations'
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Clés étrangères --
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False, index=True)
    rotation_id = db.Column(db.Integer, db.ForeignKey('rotations.id'), nullable=False, index=True)
    # -- Relations --
    rotation = db.relationship('Rotation', back_populates='challenges', lazy=True)
    challenge = db.relationship('Challenge', back_populates='rotations', lazy=True)

class Rotation(db.Model):
    __tablename__ = 'rotations'
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    name = db.Column(db.String(255), unique=True, nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    # -- Relations --
    challenges = db.relationship('ChallengeRotation', back_populates='rotation', lazy=True)
    # -- Propriétés --
    @hybrid_property
    def is_active(self):
        now = datetime.now()
        return self.start_time <= now <= self.end_time
    @is_active.expression
    def is_active(cls):
        now = datetime.now()
        return (cls.start_time <= now) & (cls.end_time >= now)

class ChallengeFiles(db.Model):
    __tablename__ = "challenge_files"
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    file_type = db.Column(db.String(32), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(255), nullable=False)
    file_role = db.Column(db.String(32), nullable=False)
    sha256 = db.Column(db.String(64), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    # -- Clé étrangère --
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    # -- Relations --
    challenge = db.relationship('Challenge', back_populates='files', lazy=True)