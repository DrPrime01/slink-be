from core import db, app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class ShortUrls(db.Model):
    __tablename__ = "short_urls"
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_id = db.Column(db.String(255), nullable=False, unique=True)
    short_url = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(
        db.DateTime(), default=datetime.utcnow(), nullable=False)
    # Foreign key for the user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('Users', back_populates='urls')

    def to_dict(self):
        return {
            'id': self.id,
            'original_url': self.original_url,
            'short_id': self.short_id,
            "short_url": self.short_url,
            # assuming created_at is a datetime object
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Users(db.Model):
    """Model for users"""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, index=True)
    email = db.Column(db.String(255), unique=True, index=True)
    password_hash = db.Column(db.String(255))

    urls = db.relationship('ShortUrls', back_populates='user', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


def init_db():
    with app.app_context():
        db.create_all()
