"""Pre/Post assessment routes."""

import json
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from app import db
from app.models.assessment import Question, Answer, Assessment, AssessmentResult
from app.models.module import Module, Progress
from app.services.AdaptiveRuleEngine import AdaptiveRuleEngine
from app.services.gamification_service import award_xp, award_badge, unlock_achievement

assessment_bp = Blueprint("assessment", __name__)

DOMAINS = [
    "phishing", "social_engineering", "password_security",
    "safe_browsing", "pretexting", "data_handling", "incident_reporting",
]


@assessment_bp.route("/pre", methods=["GET"])
@login_required
def pre_assessment():
    if current_user.pre_assessment_done:
        flash("You have already completed the pre-assessment.", "info")
        return redirect(url_for("dashboard.home"))

    questions = []
    for domain in DOMAINS:
        qs = Question.query.filter_by(domain=domain, difficulty="beginner").all()
        questions.extend(qs[:2])  # 2 per domain = 14 total

    # Attach answers to each question
    for q in questions:
        q.answer_list = Answer.query.filter_by(question_id=q.id).all()

    return render_template("assessment/pre_assessment.html", questions=questions)


@assessment_bp.route("/pre/submit", methods=["POST"])
@login_required
def submit_pre_assessment():
    if current_user.pre_assessment_done:
        return redirect(url_for("dashboard.home"))

    form_data = request.form
    questions = Question.query.all()
    q_map = {q.id: q for q in questions}

    # Tally per-domain results
    domain_correct = {d: 0 for d in DOMAINS}
    domain_total = {d: 0 for d in DOMAINS}

    for key, answer_id in form_data.items():
        if not key.startswith("q_"):
            continue
        try:
            q_id = int(key[2:])
            a_id = int(answer_id)
        except ValueError:
            continue
        q = q_map.get(q_id)
        if not q:
            continue
        answer = Answer.query.get(a_id)
        domain_total[q.domain] = domain_total.get(q.domain, 0) + 1
        if answer and answer.is_correct:
            domain_correct[q.domain] = domain_correct.get(q.domain, 0) + 1

    # Calculate domain scores as percentages
    domain_scores = {}
    for d in DOMAINS:
        total = domain_total.get(d, 1)
        correct = domain_correct.get(d, 0)
        domain_scores[d] = round((correct / total) * 100, 1) if total > 0 else 0.0

    # Run adaptive rule engine
    engine_output = AdaptiveRuleEngine.build_learning_path(domain_scores)

    # Persist assessment
    assessment = Assessment(
        user_id=current_user.id,
        assessment_type="pre",
        overall_score=engine_output["overall_score"],
        risk_level=engine_output["risk_level"],
        weakest_domain=engine_output["weakest_domain"],
    )
    db.session.add(assessment)
    db.session.flush()

    for domain, score in domain_scores.items():
        result = AssessmentResult(
            assessment_id=assessment.id,
            domain=domain,
            score=score,
            correct=domain_correct[domain],
            total=domain_total[domain],
            level_assigned=engine_output["domain_levels"].get(domain, "beginner"),
        )
        db.session.add(result)

    # Update user profile
    current_user.pre_assessment_done = True
    current_user.experience_level = AdaptiveRuleEngine.assign_level(engine_output["overall_score"])
    current_user.risk_level = engine_output["risk_level"]

    # Initialise module progress (ordered by weakness)
    modules = Module.query.order_by(Module.order).all()
    module_order_map = {m.order: m for m in modules}
    priority_module_ids = engine_output["module_order"]

    for i, mod_order in enumerate(priority_module_ids):
        m = module_order_map.get(mod_order)
        if not m:
            continue
        status = "available" if i == 0 else "locked"
        existing = Progress.query.filter_by(user_id=current_user.id, module_id=m.id).first()
        if not existing:
            level = engine_output["domain_levels"].get(m.domain, "beginner")
            prog = Progress(
                user_id=current_user.id,
                module_id=m.id,
                status=status,
                current_difficulty=level,
            )
            db.session.add(prog)

    # Award XP and badge if score ≥ 75
    award_xp(current_user, 20, "Completed pre-assessment")
    if engine_output["overall_score"] >= 75:
        award_badge(current_user, "Assessment Champion")
        unlock_achievement(current_user, "Assessment Champion",
                           "Scored ≥75% in the pre-assessment", "fa-star")

    db.session.commit()

    # Store results in session for the result page
    session["assessment_result"] = {
        "domain_scores": domain_scores,
        "engine_output": engine_output,
        "assessment_id": assessment.id,
    }

    return redirect(url_for("assessment.assessment_result"))


@assessment_bp.route("/result")
@login_required
def assessment_result():
    data = session.get("assessment_result")
    if not data:
        return redirect(url_for("dashboard.home"))

    domain_scores = data["domain_scores"]
    engine_output = data["engine_output"]

    # Pretty labels
    domain_labels = {
        "phishing": "Phishing", "social_engineering": "Social Engineering",
        "password_security": "Password Security", "safe_browsing": "Safe Browsing",
        "pretexting": "Pretexting", "data_handling": "Data Handling",
        "incident_reporting": "Incident Reporting",
    }

    chart_labels = [domain_labels.get(d, d) for d in DOMAINS]
    chart_data = [domain_scores.get(d, 0) for d in DOMAINS]

    # Build domain_results list for the table
    domain_results = []
    for d in DOMAINS:
        score = domain_scores.get(d, 0)
        domain_results.append({
            "domain": d,
            "score": score,
            "correct": 0,  # no per-question data in session; scores suffice
            "total": 2,
            "level_assigned": engine_output["domain_levels"].get(d, "beginner"),
        })

    # Build recommendations list
    recommendations = []
    for d in engine_output.get("priority_order", DOMAINS):
        level = engine_output["domain_levels"].get(d, "beginner")
        reason_map = {
            "beginner": "Needs foundational work — prioritised for early training.",
            "intermediate": "Developing skill — reinforcement scenarios recommended.",
            "advanced": "Strong knowledge — maintenance practice advised.",
        }
        recommendations.append({"domain": d, "level": level, "reason": reason_map.get(level, "")})

    return render_template(
        "assessment/result.html",
        overall_score=engine_output["overall_score"],
        risk_level=engine_output["risk_level"],
        domain_results=domain_results,
        recommendations=recommendations,
        xp_awarded=20,
        chart_labels=json.dumps(chart_labels),
        chart_data=json.dumps(chart_data),
    )


@assessment_bp.route("/post", methods=["GET"])
@login_required
def post_assessment():
    """Post-assessment after completing all modules."""
    questions = []
    for domain in DOMAINS:
        qs = Question.query.filter_by(domain=domain).all()
        questions.extend(qs[:2])
    for q in questions:
        q.answer_list = Answer.query.filter_by(question_id=q.id).all()
    return render_template("assessment/post_assessment.html", questions=questions)


@assessment_bp.route("/post/submit", methods=["POST"])
@login_required
def submit_post_assessment():
    form_data = request.form
    questions = Question.query.all()
    q_map = {q.id: q for q in questions}

    domain_correct = {d: 0 for d in DOMAINS}
    domain_total = {d: 0 for d in DOMAINS}

    for key, answer_id in form_data.items():
        if not key.startswith("q_"):
            continue
        try:
            q_id = int(key[2:])
            a_id = int(answer_id)
        except ValueError:
            continue
        q = q_map.get(q_id)
        if not q:
            continue
        answer = Answer.query.get(a_id)
        domain_total[q.domain] = domain_total.get(q.domain, 0) + 1
        if answer and answer.is_correct:
            domain_correct[q.domain] = domain_correct.get(q.domain, 0) + 1

    domain_scores = {
        d: round((domain_correct[d] / max(domain_total[d], 1)) * 100, 1)
        for d in DOMAINS
    }
    engine_output = AdaptiveRuleEngine.build_learning_path(domain_scores)

    assessment = Assessment(
        user_id=current_user.id,
        assessment_type="post",
        overall_score=engine_output["overall_score"],
        risk_level=engine_output["risk_level"],
        weakest_domain=engine_output["weakest_domain"],
    )
    db.session.add(assessment)
    db.session.flush()

    for domain, score in domain_scores.items():
        result = AssessmentResult(
            assessment_id=assessment.id,
            domain=domain,
            score=score,
            correct=domain_correct[domain],
            total=domain_total[domain],
            level_assigned=engine_output["domain_levels"].get(domain, "beginner"),
        )
        db.session.add(result)

    award_xp(current_user, 50, "Completed post-assessment")
    if engine_output["overall_score"] >= 75:
        award_badge(current_user, "Cybersecurity Aware")
        unlock_achievement(current_user, "Cybersecurity Aware",
                           "Passed the post-assessment with ≥75%", "fa-shield-halved")

    db.session.commit()

    session["assessment_result"] = {
        "domain_scores": domain_scores,
        "engine_output": engine_output,
        "assessment_id": assessment.id,
        "is_post": True,
    }
    return redirect(url_for("assessment.assessment_result"))
