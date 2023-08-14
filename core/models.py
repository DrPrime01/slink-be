from core import db, app
from datetime import datetime


class ShortUrls(db.Model):
    __tablename__ = "short_urls"
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_id = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(
        db.DateTime(), default=datetime.now(), nullable=False)


def init_db():
    with app.app_context():
        db.create_all()
