"""Scenario engine routes."""

import time as _time

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.module import Module, Scenario, ScenarioOption, Progress, AttemptHistory
from app.models.feedback import LearningActivity
from app.services.AdaptiveRuleEngine import AdaptiveRuleEngine
from app.services.gamification_service import award_xp, unlock_achievement

scenarios_bp = Blueprint("scenarios", __name__)


@scenarios_bp.route("/scenario/<int:scenario_id>")
@login_required
def scenario_player(scenario_id):
    scenario = Scenario.query.get_or_404(scenario_id)
    progress = Progress.query.filter_by(
        user_id=current_user.id, module_id=scenario.module_id
    ).first()
    options = ScenarioOption.query.filter_by(scenario_id=scenario.id).all()
    return render_template(
        "scenarios/scenario_player.html",
        scenario=scenario,
        options=options,
        progress=progress,
    )


@scenarios_bp.route("/scenario/<int:scenario_id>/submit", methods=["POST"])
@login_required
def submit_scenario(scenario_id):
    scenario = Scenario.query.get_or_404(scenario_id)
    option_id = request.form.get("option_id", type=int)
    selected = ScenarioOption.query.get(option_id) if option_id else None
    is_correct = selected.is_correct if selected else False

    progress = Progress.query.filter_by(
        user_id=current_user.id, module_id=scenario.module_id
    ).first()

    old_difficulty = progress.current_difficulty if progress else "beginner"
    difficulty_changed = False
    new_difficulty = old_difficulty
    new_hints_enabled = False

    if progress:
        streaks = AdaptiveRuleEngine.update_streaks(
            is_correct, progress.correct_streak, progress.wrong_streak
        )
        progress.correct_streak = streaks["correct_streak"]
        progress.wrong_streak = streaks["wrong_streak"]

        adjustment = AdaptiveRuleEngine.adjust_difficulty(
            progress.current_difficulty, progress.correct_streak, progress.wrong_streak
        )
        new_difficulty = adjustment["new_difficulty"]
        new_hints_enabled = adjustment["hints_enabled"]
        if new_difficulty != old_difficulty or new_hints_enabled != progress.hints_enabled:
            difficulty_changed = True
        progress.current_difficulty = new_difficulty
        progress.hints_enabled = new_hints_enabled

    # Calculate time on task from hidden start_time field (ms timestamp)
    time_taken = 0
    start_ms = request.form.get("start_time", type=int)
    if start_ms:
        elapsed = int(_time.time() * 1000) - start_ms
        time_taken = max(0, min(elapsed // 1000, scenario.time_limit or 300))

    # Log attempt in AttemptHistory
    attempt = AttemptHistory(
        user_id=current_user.id,
        module_id=scenario.module_id,
        scenario_id=scenario.id,
        answer_given=selected.text if selected else "",
        is_correct=is_correct,
        difficulty_at_time=new_difficulty,
    )
    db.session.add(attempt)

    # Log in LearningActivity for growth tracking
    activity = LearningActivity(
        user_id=current_user.id,
        activity_type="scenario_attempt",
        module_id=scenario.module_id,
        scenario_id=scenario.id,
        difficulty_level=new_difficulty,
        is_correct=is_correct,
        time_taken_seconds=time_taken,
        xp_earned=scenario.xp_reward if is_correct else 0,
    )
    db.session.add(activity)

    xp_awarded = 0
    if is_correct:
        xp_awarded = scenario.xp_reward
        award_xp(current_user, xp_awarded, f"Scenario: {scenario.title}")

    streak_message = None
    if progress:
        if progress.correct_streak >= 3:
            streak_message = f"You're on a {progress.correct_streak}-answer correct streak! Keep it up."
        if progress.correct_streak >= 10:
            unlock_achievement(current_user, "Streak Master",
                               "Answered 10 questions correctly in a row", "fa-fire")

    db.session.commit()

    # Next scenario in the same module
    next_scenario = Scenario.query.filter(
        Scenario.module_id == scenario.module_id,
        Scenario.id > scenario.id
    ).order_by(Scenario.id).first()

    return render_template(
        "scenarios/feedback.html",
        scenario=scenario,
        selected=selected,
        is_correct=is_correct,
        xp_awarded=xp_awarded,
        difficulty_changed=difficulty_changed,
        new_difficulty=new_difficulty,
        new_hints_enabled=new_hints_enabled,
        streak_message=streak_message,
        next_scenario=next_scenario,
        progress=progress,
    )
