"""Badge, Achievement, Leaderboard models."""

from datetime import datetime
from app import db


class Badge(db.Model):
    __tablename__ = "badges"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, default="")
    icon = db.Column(db.String(60), default="fa-medal")
    color = db.Column(db.String(20), default="#f59e0b")
    badge_type = db.Column(db.String(30), default="module")  # module/achievement/special

    user_badges = db.relationship("UserBadge", backref="badge", lazy="dynamic")


class UserBadge(db.Model):
    __tablename__ = "user_badges"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey("badges.id"), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "badge_id"),)


class Achievement(db.Model):
    __tablename__ = "achievements"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, default="")
    icon = db.Column(db.String(60), default="fa-trophy")
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)


class Leaderboard(db.Model):
    __tablename__ = "leaderboard"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    xp = db.Column(db.Integer, default=0)
    modules_completed = db.Column(db.Integer, default=0)
    badges_count = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("leaderboard_entry", uselist=False))
