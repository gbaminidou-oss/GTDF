"""Learning module routes."""

import json
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.module import Module, Lesson, Scenario, Progress
from app.models.feedback import LearningActivity
from app.services.gamification_service import award_xp, award_badge, unlock_achievement

modules_bp = Blueprint("modules", __name__)


@modules_bp.route("/")
@login_required
def learning_path():
    modules = Module.query.order_by(Module.order).all()
    progress_map = {
        p.module_id: p
        for p in Progress.query.filter_by(user_id=current_user.id).all()
    }

    modules_with_progress = []
    for m in modules:
        p = progress_map.get(m.id)
        modules_with_progress.append({
            "module": m,
            "progress": p,
            "status": p.status if p else "locked",
        })

    completed_count = sum(1 for mp in modules_with_progress if mp["status"] == "completed")
    total = len(modules)
    overall_pct = round((completed_count / total) * 100) if total else 0

    return render_template(
        "modules/learning_path.html",
        modules_with_progress=modules_with_progress,
        completed_count=completed_count,
        total=total,
        overall_pct=overall_pct,
    )


@modules_bp.route("/<int:module_id>")
@login_required
def module_detail(module_id):
    module = Module.query.get_or_404(module_id)
    progress = Progress.query.filter_by(user_id=current_user.id, module_id=module_id).first()

    if not progress or progress.status == "locked":
        flash("Complete the previous module to unlock this one.", "warning")
        return redirect(url_for("modules.learning_path"))

    lessons = Lesson.query.filter_by(module_id=module_id).order_by(Lesson.order).all()
    for lesson in lessons:
        try:
            lesson.key_points_parsed = json.loads(lesson.key_points or "[]")
        except Exception:
            lesson.key_points_parsed = []

    scenarios = Scenario.query.filter_by(module_id=module_id).order_by(Scenario.id).all()

    if progress.status == "available":
        progress.status = "in_progress"
        db.session.commit()

    # Log a lesson_view activity for each lesson on first visit to this module
    already_logged_ids = {
        a.lesson_id for a in LearningActivity.query.filter_by(
            user_id=current_user.id,
            activity_type="lesson_view",
            module_id=module_id,
        ).all()
        if a.lesson_id
    }
    new_lesson_views = [
        LearningActivity(
            user_id=current_user.id,
            activity_type="lesson_view",
            module_id=module_id,
            lesson_id=lesson.id,
        )
        for lesson in lessons
        if lesson.id not in already_logged_ids
    ]
    if new_lesson_views:
        db.session.add_all(new_lesson_views)
        db.session.commit()

    return render_template(
        "modules/module_detail.html",
        module=module,
        lessons=lessons,
        scenarios=scenarios,
        progress=progress,
    )


@modules_bp.route("/<int:module_id>/complete", methods=["POST"])
@login_required
def complete_module(module_id):
    module = Module.query.get_or_404(module_id)
    progress = Progress.query.filter_by(user_id=current_user.id, module_id=module_id).first()

    if not progress or progress.status not in ("in_progress", "available"):
        return redirect(url_for("modules.learning_path"))

    progress.status = "completed"
    progress.completed_at = datetime.utcnow()
    progress.xp_earned = module.xp_reward

    award_xp(current_user, module.xp_reward, f"Completed module: {module.title}")
    if module.badge_name:
        award_badge(current_user, module.badge_name)
        unlock_achievement(
            current_user,
            f"Completed: {module.title}",
            f"Finished the {module.title} module",
            module.icon,
        )

    # Unlock next module
    next_module = Module.query.filter_by(order=module.order + 1).first()
    if next_module:
        next_prog = Progress.query.filter_by(
            user_id=current_user.id, module_id=next_module.id
        ).first()
        if next_prog and next_prog.status == "locked":
            next_prog.status = "available"

    # GTDF Graduate badge
    all_progress = Progress.query.filter_by(user_id=current_user.id).all()
    all_modules_count = Module.query.count()
    if sum(1 for p in all_progress if p.status == "completed") >= all_modules_count:
        award_badge(current_user, "GTDF Graduate")
        unlock_achievement(current_user, "GTDF Graduate",
                           "Completed all 7 cybersecurity modules!", "fa-graduation-cap")

    db.session.commit()
    flash(f"Module complete! You earned {module.xp_reward} XP.", "success")
    return redirect(url_for("modules.learning_path"))
