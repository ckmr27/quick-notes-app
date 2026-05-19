import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, session, flash
from flask_login import logout_user, current_user
from app.extensions import db, login_manager, limiter
from app.models import User

load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__)
    
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback-dev-secret-key-12345")
    
    # Resolve SQLite db paths cleanly
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        db_url = f"sqlite:///{os.path.join(base_dir, 'notes.db')}"
    elif db_url.startswith("sqlite:///"):
        db_path = db_url[10:]
        if not os.path.isabs(db_path):
            db_url = f"sqlite:///{os.path.abspath(os.path.join(base_dir, '..', db_path))}"
            
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
    
    if test_config:
        app.config.update(test_config)
    
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
        
    # Blueprints
    from app.auth import auth as auth_bp
    from app.notes import notes as notes_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(notes_bp)
    
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=20)
    
    @app.before_request
    def check_session_timeout():
        if not current_user.is_authenticated:
            return
            
        session.permanent = True
        now = datetime.utcnow()
        last_active = session.get("last_active")
        
        if last_active:
            try:
                last_dt = datetime.fromisoformat(last_active)
                if now - last_dt > timedelta(minutes=20):
                    logout_user()
                    session.clear()
                    flash("Your session has expired due to 20 minutes of inactivity. Please log in again.", "danger")
                    return redirect(url_for("auth.login"))
            except ValueError:
                pass
                
        session["last_active"] = now.isoformat()
    
    @app.route("/")
    def index():
        return redirect(url_for("notes.dashboard"))
        
    with app.app_context():
        db.create_all()
        
    from flask_limiter.errors import RateLimitExceeded

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_exceeded(e):
        flash("Too many requests from your IP. Please try again later.", "danger")
        return redirect(url_for("auth.login")), 429

    return app
