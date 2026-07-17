"""User model with gamification fields."""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # Profile
    full_name = db.Column(db.String(120), default="")
    experience_level = db.Column(db.String(20), default="beginner")  # beginner/intermediate/advanced
    risk_level = db.Column(db.String(20), default="unknown")          # low/medium/high

    # Gamification
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    streak = db.Column(db.Integer, default=0)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)

    # Status
    pre_assessment_done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assessments = db.relationship("Assessment", backref="user", lazy="dynamic")
    progress = db.relationship("Progress", backref="user", lazy="dynamic")
    badges = db.relationship("UserBadge", backref="user", lazy="dynamic")
    achievements = db.relationship("Achievement", backref="user", lazy="dynamic")
    attempt_history = db.relationship("AttemptHistory", backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_xp(self, amount):
        self.xp += amount
        # Level up every 100 XP
        new_level = (self.xp // 100) + 1
        if new_level > self.level:
            self.level = new_level
        self.last_activity = datetime.utcnow()

    @property
    def xp_in_current_level(self):
        return self.xp % 100

    @property
    def xp_progress_pct(self):
        return self.xp_in_current_level

    def __repr__(self):
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
