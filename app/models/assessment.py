"""Assessment, Question, and Answer models."""

from datetime import datetime
from app import db


class Assessment(db.Model):
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assessment_type = db.Column(db.String(10), default="pre")  # pre / post
    overall_score = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(20), default="unknown")
    weakest_domain = db.Column(db.String(50), default="")
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    results = db.relationship("AssessmentResult", backref="assessment", lazy="dynamic")

    def __repr__(self):
        return f"<Assessment {self.id} user={self.user_id} type={self.assessment_type}>"


class AssessmentResult(db.Model):
    __tablename__ = "assessment_results"

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"), nullable=False)
    domain = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Float, default=0.0)        # percentage 0-100
    correct = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    level_assigned = db.Column(db.String(20), default="beginner")  # from rule engine


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), default="beginner")  # beginner/intermediate/advanced
    text = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, default="")
    points = db.Column(db.Integer, default=10)

    answers = db.relationship("Answer", backref="question", lazy="dynamic")


class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
