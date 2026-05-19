from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, limiter
from app.models import User

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per 15 minutes", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("notes.dashboard"))
        
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if not username or not password:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("auth.login"))
            
        if len(username) > 150 or len(password) > 128:
            flash("Invalid input. Maximum length exceeded.", "danger")
            return redirect(url_for("auth.login"))
            
        user = User.query.filter_by(username=username).first()
        if user:
            # check lockout status
            lock = user.lockout_time
            if lock:
                delta = (datetime.utcnow() - lock).total_seconds()
                if delta < 120:
                    wait_sec = int(120 - delta)
                    flash(f"Account is locked due to too many failed attempts. Try again in {wait_sec} seconds.", "danger")
                    return redirect(url_for("auth.login"))
                
                # lockout expired
                user.lockout_time = None
                user.login_attempts = 0
                db.session.commit()
            
            if check_password_hash(user.password_hash, password):
                user.login_attempts = 0
                user.lockout_time = None
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for("notes.dashboard"))
            
            user.login_attempts += 1
            if user.login_attempts >= 5:
                user.lockout_time = datetime.utcnow()
                flash("Too many failed attempts. Your account has been locked for 2 minutes.", "danger")
            else:
                flash(f"Invalid username or password. {5 - user.login_attempts} attempt(s) remaining.", "danger")
            db.session.commit()
        else:
            flash("Invalid username or password.", "danger")
            
    return render_template("login.html")

@auth.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per 15 minutes", methods=["POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("notes.dashboard"))
        
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if not username or not password or not confirm_password:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("auth.register"))
            
        if len(username) < 3 or len(username) > 150:
            flash("Username must be between 3 and 150 characters.", "danger")
            return redirect(url_for("auth.register"))
            
        if len(password) < 6 or len(password) > 128:
            flash("Password must be between 6 and 128 characters.", "danger")
            return redirect(url_for("auth.register"))
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))
            
        if User.query.filter_by(username=username).first():
            flash("Username is already taken.", "danger")
            return redirect(url_for("auth.register"))
            
        pw_hash = generate_password_hash(password, method="scrypt")
        usr = User(username=username, password_hash=pw_hash)
        
        try:
            db.session.add(usr)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "danger")
            
    return render_template("register.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
