"""Main application module.

This module initializes extensions, blueprints, and the database,
and provides a factory for creating the Flask app.
"""

# Flask imports
# Python Imports
import os
from datetime import timedelta
from importlib import import_module
from pathlib import Path

# APP Imports
from configs import Configurator, csp
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

db = SQLAlchemy()
tlsm = Talisman()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Faça login para acessar essa página."
login_manager.login_message_category = "info"


class AppFactory:
    """Factory class for creating and configuring the Flask application."""

    def init_extensions(self, app: Flask) -> None:
        """Initialize Flask extensions and middleware.

        Args:
            app (Flask): The Flask application instance.

        """
        db.init_app(app)
        mail.init_app(app)
        login_manager.init_app(app)

        with app.app_context():
            self.init_database(app, db)

            tlsm.init_app(
                app,
                content_security_policy=csp(),
                force_https_permanent=True,
                force_https=True,
                session_cookie_http_only=True,
                session_cookie_samesite="Lax",
                strict_transport_security_max_age=timedelta(days=31).max.seconds,
                x_content_type_options=True,
                x_xss_protection=True,
            )
            import_module("app.routes", __package__)

    def create_app(self) -> Flask:
        """Create and configure the Flask application.

        Returns:
            Flask: The configured Flask application.

        """
        src_path = os.path.join(os.getcwd(), "static")
        app = Flask(__name__, static_folder=src_path)

        default_config = Configurator().get_configurator()

        app.config.from_object(default_config)
        self.init_extensions(app)
        self.init_blueprints(app)

        # Initialize logs module
        from web.logs.setup import initialize_logging

        app.logger = initialize_logging()

        return app

    def init_blueprints(self, app: Flask) -> None:
        """Register blueprints with the Flask application.

        Args:
            app (Flask): The Flask application instance.

        """
        from web.routes.auth import auth
        from web.routes.bot import bot
        from web.routes.config import admin, supersu, usr
        from web.routes.credentials import cred
        from web.routes.dashboard import dash
        from web.routes.execution import exe
        from web.routes.logs import logsbot

        listBlueprints = [bot, auth, logsbot, exe, dash, cred, admin, supersu, usr]  # noqa: N806

        for bp in listBlueprints:
            app.register_blueprint(bp)

    def init_database(self, app: Flask, db: SQLAlchemy) -> None:
        """Initialize the database schema if not already created.

        Args:
            app (Flask): The Flask application instance.
            db (SQLAlchemy): The SQLAlchemy database instance.

        """
        from web.models import init_database

        if not Path("is_init.txt").exists():
            with open("is_init.txt", "w") as f:
                f.write(f"{init_database(app, db)}")

        from web.models import Users

        if not db.engine.dialect.has_table(db.engine.connect(), Users.__tablename__):
            with open("is_init.txt", "w") as f:
                f.write(f"{init_database(app, db)}")


create_app = AppFactory().create_app
