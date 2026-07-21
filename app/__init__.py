"""
GTDF Platform — Application Factory
"""

import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

_db_initialised = False


def create_app(config_name="default"):
    from config import config

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config[config_name])

    # Initialise extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    # Import all models so SQLAlchemy metadata is complete before any create_all
    import app.models.user          # noqa: F401
    import app.models.module        # noqa: F401
    import app.models.assessment    # noqa: F401
    import app.models.gamification  # noqa: F401
    import app.models.feedback      # noqa: F401

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.assessment import assessment_bp
    from app.routes.modules import modules_bp
    from app.routes.scenarios import scenarios_bp
    from app.routes.gamification import gamification_bp
    from app.routes.feedback import feedback_bp
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(assessment_bp, url_prefix="/assessment")
    app.register_blueprint(modules_bp, url_prefix="/modules")
    app.register_blueprint(scenarios_bp, url_prefix="/scenarios")
    app.register_blueprint(gamification_bp, url_prefix="/gamification")
    app.register_blueprint(feedback_bp, url_prefix="/feedback")

    # Defer DB creation to first request so gunicorn always starts successfully
    @app.before_request
    def _init_db_once():
        global _db_initialised
        if _db_initialised:
            return
        _db_initialised = True
        try:
            db.create_all()
            print("[GTDF] db.create_all() completed", file=sys.stderr)
        except Exception as exc:
            print(f"[GTDF] db.create_all() failed: {exc}", file=sys.stderr)
            return
        try:
            from app.database.seed import seed_all
            seed_all()
            print("[GTDF] Seed completed", file=sys.stderr)
        except Exception as exc:
            db.session.rollback()
            print(f"[GTDF] Seed skipped or failed: {exc}", file=sys.stderr)

    return app
