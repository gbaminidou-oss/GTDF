"""Module, Lesson, Scenario, Progress models."""

from datetime import datetime
from app import db


class Module(db.Model):
    __tablename__ = "modules"

    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer, nullable=False)
    domain = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")
    icon = db.Column(db.String(60), default="fa-shield-alt")
    color = db.Column(db.String(20), default="#2563eb")
    xp_reward = db.Column(db.Integer, default=50)
    badge_name = db.Column(db.String(80), default="")

    lessons = db.relationship("Lesson", backref="module", lazy="dynamic", order_by="Lesson.order")
    scenarios = db.relationship("Scenario", backref="module", lazy="dynamic")
    progress = db.relationship("Progress", backref="module", lazy="dynamic")


class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    key_points = db.Column(db.Text, default="")   # JSON list stored as text


class Scenario(db.Model):
    __tablename__ = "scenarios"

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    scenario_type = db.Column(db.String(30), default="email")  # email/sms/website/usb/phone
    description = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text, default="")  # rendered fake artefact
    question = db.Column(db.Text, nullable=False)
    correct_action = db.Column(db.String(20), nullable=False)  # report/ignore/delete/verify
    explanation = db.Column(db.Text, default="")
    difficulty = db.Column(db.String(20), default="beginner")
    time_limit = db.Column(db.Integer, default=60)   # seconds
    xp_reward = db.Column(db.Integer, default=25)

    options = db.relationship("ScenarioOption", backref="scenario", lazy="dynamic")


class ScenarioOption(db.Model):
    __tablename__ = "scenario_options"

    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenarios.id"), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    feedback = db.Column(db.Text, default="")


class Progress(db.Model):
    __tablename__ = "progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)
    status = db.Column(db.String(20), default="locked")   # locked/available/in_progress/completed
    current_difficulty = db.Column(db.String(20), default="beginner")
    correct_streak = db.Column(db.Integer, default=0)
    wrong_streak = db.Column(db.Integer, default=0)
    hints_enabled = db.Column(db.Boolean, default=False)
    score = db.Column(db.Float, default=0.0)
    xp_earned = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime, nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "module_id"),)


class AttemptHistory(db.Model):
    __tablename__ = "attempt_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenarios.id"), nullable=True)
    answer_given = db.Column(db.String(200), default="")
    is_correct = db.Column(db.Boolean, default=False)
    difficulty_at_time = db.Column(db.String(20), default="beginner")
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)
