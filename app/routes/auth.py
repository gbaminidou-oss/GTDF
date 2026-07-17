"""Authentication routes — register, login, logout, profile, settings."""

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.gamification import Leaderboard

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        full_name = request.form.get("full_name", "").strip()

        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if not email or "@" not in email:
            errors.append("Please enter a valid email address.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if User.query.filter_by(username=username).first():
            errors.append("Username already taken.")
        if User.query.filter_by(email=email).first():
            errors.append("Email already registered.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("auth/register.html", username=username, email=email, full_name=full_name)

        try:
            user = User(username=username, email=email, full_name=full_name)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            lb = Leaderboard(user_id=user.id, xp=0)
            db.session.add(lb)
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            flash("Registration failed due to a server error. Please try again.", "error")
            import sys
            print(f"[GTDF] Register error: {exc}", file=sys.stderr)
            return render_template("auth/register.html", username=username, email=email, full_name=full_name)

        login_user(user)
        flash("Welcome to GTDF! Start with your pre-assessment.", "success")
        return redirect(url_for("assessment.pre_assessment"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if not user or not user.check_password(password):
            flash("Invalid username/email or password.", "error")
            return render_template("auth/login.html", identifier=identifier)

        login_user(user, remember=remember)
        next_page = request.args.get("next")
        flash(f"Welcome back, {user.username}!", "success")
        return redirect(next_page or url_for("dashboard.home"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.full_name = request.form.get("full_name", "").strip()
        new_email = request.form.get("email", "").strip().lower()
        if new_email and new_email != current_user.email:
            if User.query.filter_by(email=new_email).first():
                flash("Email already in use.", "error")
                return redirect(url_for("auth.profile"))
            current_user.email = new_email
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("auth.profile"))
    return render_template("auth/profile.html")


@auth_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "change_password":
            current_pw = request.form.get("current_password", "")
            new_pw = request.form.get("new_password", "")
            confirm_pw = request.form.get("confirm_password", "")
            if not current_user.check_password(current_pw):
                flash("Current password is incorrect.", "error")
            elif len(new_pw) < 8:
                flash("New password must be at least 8 characters.", "error")
            elif new_pw != confirm_pw:
                flash("New passwords do not match.", "error")
            else:
                current_user.set_password(new_pw)
                db.session.commit()
                flash("Password changed successfully.", "success")
    return render_template("auth/settings.html")
