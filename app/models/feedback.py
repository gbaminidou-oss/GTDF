"""LearningActivity — tracks lesson views and scenario attempts with time on task."""

from datetime import datetime
from app import db


class LearningActivity(db.Model):
    __tablename__ = "learning_activities"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    activity_type = db.Column(db.String(20), nullable=False)  # 'lesson_view' / 'scenario_attempt'
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id"), nullable=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey("scenarios.id"), nullable=True)
    difficulty_level = db.Column(db.String(20), default="")
    is_correct = db.Column(db.Boolean, nullable=True)   # null for lesson views
    time_taken_seconds = db.Column(db.Integer, default=0)
    xp_earned = db.Column(db.Integer, default=0)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LearningActivity user={self.user_id} type={self.activity_type}>"
