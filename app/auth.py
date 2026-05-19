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
        username = request.form.get("username").strip()
        password = request.form.get("password")
        
        if not username or not password:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("auth.login"))
            
        if len(username) > 150 or len(password) > 128:
            flash("Invalid input. Username or password length limit exceeded.", "danger")
            return redirect(url_for("auth.login"))
            
        user = User.query.filter_by(username=username).first()
        if user:
            # Check if user is currently locked out
            if user.lockout_time:
                time_passed = datetime.utcnow() - user.lockout_time
                if time_passed.total_seconds() < 120:
                    remaining_time = int(120 - time_passed.total_seconds())
                    flash(f"Account is locked due to too many failed attempts. Try again in {remaining_time} seconds.", "danger")
                    return redirect(url_for("auth.login"))
                else:
                    # Lockout expired
                    user.lockout_time = None
                    user.login_attempts = 0
                    db.session.commit()
            
            if check_password_hash(user.password_hash, password):
                # Reset attempts on success
                user.login_attempts = 0
                user.lockout_time = None
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for("notes.dashboard"))
            else:
                user.login_attempts += 1
                if user.login_attempts >= 5:
                    user.lockout_time = datetime.utcnow()
                    db.session.commit()
                    flash("Too many failed attempts. Your account has been locked for 2 minutes.", "danger")
                else:
                    remaining = 5 - user.login_attempts
                    db.session.commit()
                    flash(f"Invalid username or password. {remaining} attempt(s) remaining.", "danger")
        else:
            flash("Invalid username or password.", "danger")
            
    return render_template("login.html")

@auth.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per 15 minutes", methods=["POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("notes.dashboard"))
        
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        if not username or not password or not confirm_password:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("auth.register"))
            
        if len(username) > 150 or len(password) > 128 or len(confirm_password) > 128:
            flash("Invalid input. Username or password length limit exceeded.", "danger")
            return redirect(url_for("auth.register"))
            
        if len(username) < 3:
            flash("Username must be at least 3 characters long.", "danger")
            return redirect(url_for("auth.register"))
            
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return redirect(url_for("auth.register"))
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))
            
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash("Username is already taken.", "danger")
            return redirect(url_for("auth.register"))
            
        hashed_password = generate_password_hash(password, method="scrypt")
        new_user = User(username=username, password_hash=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "danger")
            
    return render_template("register.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
