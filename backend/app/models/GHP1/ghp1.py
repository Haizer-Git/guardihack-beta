from extensions import db

class GHP1_User(db.Model):
    __table_name__ = 'ghp1_users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ghp1_score = db.Column(db.Integer, default=0)

