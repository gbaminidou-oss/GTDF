"""Gamification routes — leaderboard, achievements, badges."""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.gamification import Badge, UserBadge, Achievement, Leaderboard
from app.models.module import Progress

gamification_bp = Blueprint("gamification", __name__)


@gamification_bp.route("/leaderboard")
@login_required
def leaderboard():
    entries = (
        Leaderboard.query
        .order_by(Leaderboard.xp.desc())
        .limit(20)
        .all()
    )
    # Find current user rank
    user_rank = next(
        (i + 1 for i, e in enumerate(entries) if e.user_id == current_user.id),
        None,
    )
    return render_template(
        "gamification/leaderboard.html",
        entries=entries,
        user_rank=user_rank,
    )


@gamification_bp.route("/achievements")
@login_required
def achievements():
    all_badges = Badge.query.all()
    earned_ids = {ub.badge_id for ub in UserBadge.query.filter_by(user_id=current_user.id).all()}
    badge_status = [{"badge": b, "earned": b.id in earned_ids} for b in all_badges]

    achievements_list = (
        Achievement.query
        .filter_by(user_id=current_user.id)
        .order_by(Achievement.earned_at.desc())
        .all()
    )
    return render_template(
        "gamification/achievements.html",
        badge_status=badge_status,
        achievements_list=achievements_list,
    )
