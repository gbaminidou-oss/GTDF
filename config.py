"""
GTDF Platform — Application Configuration
Design Science Research | Adaptive Cybersecurity Awareness Training
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "gtdf-dsr-secret-key-change-in-production")

    # Use Render's DATABASE_URL (Postgres) when available, fall back to SQLite locally
    _db_url = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'gtdf.db'}")
    # Render provides postgres:// but SQLAlchemy 2.x requires postgresql://
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False  # Simplified for prototype

    # Gamification constants
    XP_PER_CORRECT_ANSWER = 10
    XP_PER_MODULE_COMPLETE = 50
    XP_PER_SCENARIO_PASS = 25
    XP_LEVEL_THRESHOLD = 100  # XP needed per level

    # Adaptive rule engine thresholds (from dissertation §4.6)
    BEGINNER_MAX = 39       # score < 40% → Beginner
    INTERMEDIATE_MAX = 74   # score 40-74% → Intermediate
    ADVANCED_MIN = 75       # score ≥ 75% → Advanced

    # Dynamic difficulty adjustment (dissertation Fig 4.21)
    CORRECT_STREAK_UPGRADE = 3   # 3 consecutive correct → upgrade difficulty
    WRONG_STREAK_DOWNGRADE = 2   # 2 consecutive wrong → downgrade + hints


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
