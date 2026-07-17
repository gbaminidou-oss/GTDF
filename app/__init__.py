"""
GTDF Platform — Application Factory
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


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

    # Create all database tables
    with app.app_context():
        db.create_all()
        _seed_initial_data()

    return app


def _seed_initial_data():
    """Seed modules, questions and badges on first run."""
    from app.database.seed import seed_all
    seed_all()
