from datetime import datetime
# pyrefly: ignore [missing-import]
from flask_login import UserMixin
from app.extensions import db

class User(db.Model, UserMixin):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    login_attempts = db.Column(db.Integer, default=0, nullable=False)
    lockout_time = db.Column(db.DateTime, nullable=True)
    
    # Relationship to notes
    notes = db.relationship("Note", backref="author", lazy=True, cascade="all, delete-orphan")

class Note(db.Model):
    __tablename__ = "notes"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
