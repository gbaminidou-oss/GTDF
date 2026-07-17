"""Feedback & growth routes — personal progress dashboard and CSV export."""

import csv
import io
import json
from datetime import datetime

from flask import Blueprint, render_template, Response, jsonify, request
from flask_login import login_required, current_user

from app import db
from app.models.assessment import Assessment, AssessmentResult
from app.models.module import Module, Progress, AttemptHistory
from app.models.feedback import LearningActivity

feedback_bp = Blueprint("feedback", __name__)

DOMAINS = [
    "phishing", "social_engineering", "password_security",
    "safe_browsing", "pretexting", "data_handling", "incident_reporting",
]
DOMAIN_LABELS = {
    "phishing": "Phishing",
    "social_engineering": "Social Engineering",
    "password_security": "Password Security",
    "safe_browsing": "Safe Browsing",
    "pretexting": "Pretexting",
    "data_handling": "Data Handling",
    "incident_reporting": "Incident Reporting",
}


def _build_user_stats(user):
    """Compile all growth metrics for a given user."""
    # ── Assessments ──────────────────────────────────────────────────
    pre = (Assessment.query
           .filter_by(user_id=user.id, assessment_type="pre")
           .order_by(Assessment.id).first())
    post = (Assessment.query
            .filter_by(user_id=user.id, assessment_type="post")
            .order_by(Assessment.id.desc()).first())

    pre_results = {r.domain: r.score for r in pre.results.all()} if pre else {}
    post_results = {r.domain: r.score for r in post.results.all()} if post else {}

    pre_overall = pre.overall_score if pre else 0.0
    post_overall = post.overall_score if post else None

    # Per-domain improvement
    domain_data = []
    for d in DOMAINS:
        pre_s = pre_results.get(d, 0.0)
        post_s = post_results.get(d) if post else None
        delta = round(post_s - pre_s, 1) if post_s is not None else None
        domain_data.append({
            "key": d,
            "label": DOMAIN_LABELS[d],
            "pre": pre_s,
            "post": post_s,
            "delta": delta,
        })

    # ── Scenario attempts (from AttemptHistory) ───────────────────────
    attempts = (AttemptHistory.query
                .filter_by(user_id=user.id)
                .filter(AttemptHistory.scenario_id.isnot(None))
                .order_by(AttemptHistory.attempted_at)
                .all())
    total_attempts = len(attempts)
    correct_attempts = sum(1 for a in attempts if a.is_correct)
    accuracy_pct = round(correct_attempts / total_attempts * 100, 1) if total_attempts else 0.0

    # ── LearningActivity (time on task) ──────────────────────────────
    activities = (LearningActivity.query
                  .filter_by(user_id=user.id)
                  .order_by(LearningActivity.recorded_at)
                  .all())
    total_seconds = sum(a.time_taken_seconds for a in activities if a.time_taken_seconds)
    total_minutes = round(total_seconds / 60, 1)

    lesson_views = sum(1 for a in activities if a.activity_type == "lesson_view")

    # ── Module progress ───────────────────────────────────────────────
    progress_records = Progress.query.filter_by(user_id=user.id).all()
    completed_modules = sum(1 for p in progress_records if p.status == "completed")

    # ── Timeline: last 20 scenario attempts for the activity feed ─────
    recent_attempts = attempts[-20:] if len(attempts) > 20 else attempts
    timeline = []
    for a in reversed(recent_attempts):
        timeline.append({
            "date": a.attempted_at.strftime("%d %b %Y, %H:%M"),
            "is_correct": a.is_correct,
            "difficulty": a.difficulty_at_time,
            "module_id": a.module_id,
        })

    # ── Difficulty progression counts ─────────────────────────────────
    diff_counts = {"beginner": 0, "intermediate": 0, "advanced": 0}
    for a in attempts:
        d = a.difficulty_at_time or "beginner"
        diff_counts[d] = diff_counts.get(d, 0) + 1

    return {
        "pre": pre,
        "post": post,
        "pre_overall": pre_overall,
        "post_overall": post_overall,
        "has_post": post is not None,
        "overall_improvement": round(post_overall - pre_overall, 1) if post_overall is not None else None,
        "domain_data": domain_data,
        "total_attempts": total_attempts,
        "correct_attempts": correct_attempts,
        "accuracy_pct": accuracy_pct,
        "total_minutes": total_minutes,
        "lesson_views": lesson_views,
        "completed_modules": completed_modules,
        "total_modules": 7,
        "timeline": timeline,
        "diff_counts": diff_counts,
        "xp": user.xp,
        "level": user.level,
    }


@feedback_bp.route("/growth")
@login_required
def growth():
    stats = _build_user_stats(current_user)

    # JSON for charts
    chart_labels = json.dumps([DOMAIN_LABELS[d] for d in DOMAINS])
    pre_data = json.dumps([stats["domain_data"][i]["pre"] for i in range(len(DOMAINS))])
    post_data = json.dumps([
        stats["domain_data"][i]["post"] if stats["domain_data"][i]["post"] is not None else "null"
        for i in range(len(DOMAINS))
    ])
    delta_data = json.dumps([
        stats["domain_data"][i]["delta"] if stats["domain_data"][i]["delta"] is not None else 0
        for i in range(len(DOMAINS))
    ])
    diff_labels = json.dumps(["Beginner", "Intermediate", "Advanced"])
    diff_data = json.dumps([
        stats["diff_counts"]["beginner"],
        stats["diff_counts"]["intermediate"],
        stats["diff_counts"]["advanced"],
    ])

    return render_template(
        "feedback/growth.html",
        stats=stats,
        chart_labels=chart_labels,
        pre_data=pre_data,
        post_data=post_data,
        delta_data=delta_data,
        diff_labels=diff_labels,
        diff_data=diff_data,
    )


@feedback_bp.route("/export.csv")
@login_required
def export_csv():
    """Download the current user's complete feedback dataset as CSV."""
    stats = _build_user_stats(current_user)

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    header = [
        "username", "email", "full_name",
        "risk_level", "experience_level", "xp", "level",
        "pre_overall_score",
    ]
    for d in DOMAINS:
        header.append(f"pre_{d}")
    header += ["post_overall_score"]
    for d in DOMAINS:
        header.append(f"post_{d}")
    for d in DOMAINS:
        header.append(f"delta_{d}")
    header += [
        "modules_completed", "total_modules",
        "scenarios_attempted", "correct_answers", "accuracy_pct",
        "lesson_views", "total_time_minutes",
        "beginner_attempts", "intermediate_attempts", "advanced_attempts",
        "pre_assessment_date", "post_assessment_date",
    ]
    writer.writerow(header)

    # Data row
    row = [
        current_user.username,
        current_user.email,
        getattr(current_user, "full_name", ""),
        current_user.risk_level,
        current_user.experience_level,
        stats["xp"],
        stats["level"],
        stats["pre_overall"],
    ]
    domain_map = {d["key"]: d for d in stats["domain_data"]}
    for d in DOMAINS:
        row.append(domain_map[d]["pre"])
    row.append(stats["post_overall"] if stats["post_overall"] is not None else "")
    for d in DOMAINS:
        row.append(domain_map[d]["post"] if domain_map[d]["post"] is not None else "")
    for d in DOMAINS:
        row.append(domain_map[d]["delta"] if domain_map[d]["delta"] is not None else "")
    row += [
        stats["completed_modules"],
        stats["total_modules"],
        stats["total_attempts"],
        stats["correct_attempts"],
        stats["accuracy_pct"],
        stats["lesson_views"],
        stats["total_minutes"],
        stats["diff_counts"]["beginner"],
        stats["diff_counts"]["intermediate"],
        stats["diff_counts"]["advanced"],
        stats["pre"].completed_at.strftime("%Y-%m-%d %H:%M") if stats["pre"] else "",
        stats["post"].completed_at.strftime("%Y-%m-%d %H:%M") if stats["post"] else "",
    ]
    writer.writerow(row)

    output.seek(0)
    filename = f"gtdf_growth_{current_user.username}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@feedback_bp.route("/lesson/<int:lesson_id>/view", methods=["POST"])
@login_required
def log_lesson_view(lesson_id):
    """Called via fetch() when a user reads a lesson."""
    from app.models.module import Lesson
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({"ok": False}), 404

    activity = LearningActivity(
        user_id=current_user.id,
        activity_type="lesson_view",
        module_id=lesson.module_id,
        lesson_id=lesson_id,
        time_taken_seconds=request.json.get("time_seconds", 0) if request.is_json else 0,
    )
    db.session.add(activity)
    db.session.commit()
    return jsonify({"ok": True})
