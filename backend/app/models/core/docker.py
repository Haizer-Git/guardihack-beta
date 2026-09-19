from extensions import db
from datetime import datetime

class DockerImage(db.Model):
    __tablename__ = 'docker_images'
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    name = db.Column(db.String(255), unique=True, nullable=False)
    image_tag = db.Column(db.String(255), nullable=False)
    internal_port = db.Column(db.Integer, nullable=False, default=80)
    memory_limit = db.Column(db.String(50), nullable=False, default='256m')
    # -- Relations --
    challenges = db.relationship('Challenge', back_populates='docker_image', lazy=True)

class UserInstance(db.Model):
    __tablename__ = "user_instances"
    # -- Clé primaire --
    id = db.Column(db.Integer, primary_key=True)
    # -- Colonnes --
    container_name = db.Column(db.String(255), nullable=False)
    subdomain = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    # -- Clés étrangères --
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    # -- Relations --
    user = db.relationship('User', back_populates='instances', lazy=True)
    challenge = db.relationship('Challenge', back_populates='instances', lazy=True)