"""Dashboard routes."""

import json
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.module import Module, Progress
from app.models.assessment import Assessment, AssessmentResult
from app.models.gamification import UserBadge, Achievement

dashboard_bp = Blueprint("dashboard", __name__)

DOMAIN_LABELS = {
    "phishing": "Phishing", "social_engineering": "Social Engineering",
    "password_security": "Password Security", "safe_browsing": "Safe Browsing",
    "pretexting": "Pretexting", "data_handling": "Data Handling",
    "incident_reporting": "Incident Reporting",
}
DOMAINS = list(DOMAIN_LABELS.keys())


@dashboard_bp.route("/")
@login_required
def home():
    if not current_user.pre_assessment_done:
        return redirect(url_for("assessment.pre_assessment"))

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
    total_modules = len(modules)
    overall_pct = round((completed_count / total_modules) * 100) if total_modules else 0

    # Latest assessment scores for radar chart
    latest = (Assessment.query
               .filter_by(user_id=current_user.id, assessment_type="pre")
               .order_by(Assessment.id.desc()).first())

    chart_labels = json.dumps([DOMAIN_LABELS[d] for d in DOMAINS])
    chart_data = json.dumps([0.0] * len(DOMAINS))

    if latest:
        results = {r.domain: r.score for r in latest.results.all()}
        chart_data = json.dumps([results.get(d, 0) for d in DOMAINS])

    badges = UserBadge.query.filter_by(user_id=current_user.id).all()
    achievements = Achievement.query.filter_by(user_id=current_user.id)\
                                    .order_by(Achievement.earned_at.desc()).limit(3).all()

    return render_template(
        "dashboard/home.html",
        modules_with_progress=modules_with_progress,
        completed_count=completed_count,
        total_modules=total_modules,
        overall_pct=overall_pct,
        chart_labels=chart_labels,
        chart_data=chart_data,
        badges=badges,
        achievements=achievements,
    )


@dashboard_bp.route("/progress")
@login_required
def progress():
    modules = Module.query.order_by(Module.order).all()
    progress_records = {
        p.module_id: p
        for p in Progress.query.filter_by(user_id=current_user.id).all()
    }

    # Assessment history
    assessments = (Assessment.query
                   .filter_by(user_id=current_user.id)
                   .order_by(Assessment.completed_at.desc())
                   .all())

    # Build chart data for all assessments
    pre = next((a for a in assessments if a.assessment_type == "pre"), None)
    post = next((a for a in assessments if a.assessment_type == "post"), None)

    pre_scores = {}
    post_scores = {}
    if pre:
        pre_scores = {r.domain: r.score for r in pre.results.all()}
    if post:
        post_scores = {r.domain: r.score for r in post.results.all()}

    chart_labels = json.dumps([DOMAIN_LABELS[d] for d in DOMAINS])
    pre_data = json.dumps([pre_scores.get(d, 0) for d in DOMAINS])
    post_data = json.dumps([post_scores.get(d, 0) for d in DOMAINS])

    badges = UserBadge.query.filter_by(user_id=current_user.id).all()
    achievements = Achievement.query.filter_by(user_id=current_user.id)\
                                    .order_by(Achievement.earned_at.desc()).all()

    module_progress_list = []
    for m in modules:
        p = progress_records.get(m.id)
        module_progress_list.append({"module": m, "progress": p})

    return render_template(
        "dashboard/progress.html",
        module_progress_list=module_progress_list,
        assessments=assessments,
        chart_labels=chart_labels,
        pre_data=pre_data,
        post_data=post_data,
        badges=badges,
        achievements=achievements,
        has_post=post is not None,
    )
