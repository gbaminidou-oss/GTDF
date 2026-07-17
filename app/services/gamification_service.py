"""Gamification service — XP, badges, leaderboard updates."""

from datetime import datetime
from app import db
from app.models.gamification import Badge, UserBadge, Achievement, Leaderboard


def award_xp(user, amount: int, reason: str = "") -> dict:
    """Add XP to user and check for level-up. Returns event dict."""
    old_level = user.level
    user.add_xp(amount)
    leveled_up = user.level > old_level
    _sync_leaderboard(user)
    db.session.commit()
    return {"xp_gained": amount, "new_xp": user.xp, "leveled_up": leveled_up,
            "new_level": user.level, "reason": reason}


def award_badge(user, badge_name: str) -> bool:
    """Award a badge to a user if not already earned. Returns True if newly awarded."""
    badge = Badge.query.filter_by(name=badge_name).first()
    if not badge:
        return False
    existing = UserBadge.query.filter_by(user_id=user.id, badge_id=badge.id).first()
    if existing:
        return False
    ub = UserBadge(user_id=user.id, badge_id=badge.id)
    db.session.add(ub)
    _sync_leaderboard(user)
    db.session.commit()
    return True


def unlock_achievement(user, title: str, description: str, icon: str = "fa-trophy") -> bool:
    """Create an achievement record if not already present."""
    existing = Achievement.query.filter_by(user_id=user.id, title=title).first()
    if existing:
        return False
    ach = Achievement(user_id=user.id, title=title, description=description, icon=icon)
    db.session.add(ach)
    db.session.commit()
    return True


def get_leaderboard(limit: int = 10) -> list:
    """Return top N leaderboard entries with user info."""
    entries = (
        Leaderboard.query
        .order_by(Leaderboard.xp.desc())
        .limit(limit)
        .all()
    )
    return entries


def _sync_leaderboard(user):
    """Keep leaderboard table in sync with user state."""
    entry = Leaderboard.query.filter_by(user_id=user.id).first()
    if not entry:
        entry = Leaderboard(user_id=user.id)
        db.session.add(entry)
    entry.xp = user.xp
    entry.badges_count = user.badges.count()
    entry.updated_at = datetime.utcnow()
