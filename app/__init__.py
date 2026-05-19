import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, session, flash
from flask_login import logout_user, current_user
from app.extensions import db, login_manager, limiter
from app.models import User

# Load environment variables
load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Configuration loaded from environment variables
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback-dev-secret-key-12345")
    
    # Setup absolute database path for SQLite to ensure compatibility across OS
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_url = os.getenv("DATABASE_URL", "sqlite:///" + os.path.join(base_dir, "notes.db"))
    if db_url.startswith("sqlite:///"):
        db_path = db_url[10:]
        if not os.path.isabs(db_path):
            project_root = os.path.abspath(os.path.join(base_dir, ".."))
            db_url = "sqlite:///" + os.path.abspath(os.path.join(project_root, db_path))
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024
    
    if test_config:
        app.config.update(test_config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
        
    # Register blueprints
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from app.notes import notes as notes_blueprint
    app.register_blueprint(notes_blueprint)
    
    # Configure permanent session lifetime to 20 minutes
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=20)
    
    @app.before_request
    def check_session_timeout():
        if current_user.is_authenticated:
            session.permanent = True
            last_active = session.get("last_active")
            now = datetime.utcnow()
            
            if last_active:
                try:
                    last_active_dt = datetime.fromisoformat(last_active)
                    if now - last_active_dt > timedelta(minutes=20):
                        logout_user()
                        session.clear()
                        flash("Your session has expired due to 20 minutes of inactivity. Please log in again.", "danger")
                        return redirect(url_for("auth.login"))
                except ValueError:
                    pass
            
            session["last_active"] = now.isoformat()
    
    # Base URL redirect
    @app.route("/")
    def index():
        return redirect(url_for("notes.dashboard"))
        
    # Automatically create tables within application context
    with app.app_context():
        db.create_all()
        
    from flask_limiter.errors import RateLimitExceeded

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_exceeded(e):
        flash("Too many requests from your IP. Please try again later.", "danger")
        return redirect(url_for("auth.login")), 429

    return app
