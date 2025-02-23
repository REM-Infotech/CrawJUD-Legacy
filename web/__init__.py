"""Main application module.

This module initializes extensions, blueprints, and the database,
and provides a factory for creating the Quart app.
"""

# Quart imports
# Python Imports
import asyncio
import os
from datetime import timedelta
from importlib import import_module
from pathlib import Path

import quart_flask_patch  # noqa: F401
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

# APP Imports
from quart import Quart

db = SQLAlchemy()
tlsm = Talisman()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Faça login para acessar essa página."
login_manager.login_message_category = "info"

objects_config = {
    "development": "app.config.DevelopmentConfig",
    "production": "app.config.ProductionConfig",
    "testing": "app.config.TestingConfig",
}


class AppFactory:
    """Factory class for creating and configuring the Quart application."""

    def init_extensions(self, app: Quart) -> None:
        """Initialize Quart extensions and middleware.

        Args:
            app (Quart): The Quart application instance.

        """
        db.init_app(app)
        mail.init_app(app)
        login_manager.init_app(app)

        with app.app_context():
            self.init_database(app, db)

            tlsm.init_app(
                app,
                content_security_policy=app.config["CSP"],
                force_https_permanent=True,
                force_https=True,
                session_cookie_http_only=True,
                session_cookie_samesite="Lax",
                strict_transport_security_max_age=timedelta(days=31).max.seconds,
                x_content_type_options=True,
                x_xss_protection=True,
            )
            import_module("web.routes", __package__)

    def create_app(self) -> Quart:
        """Create and configure the Quart application.

        Returns:
            Quart: The configured Quart application.

        """
        src_path = str(Path(__file__).parent.resolve().joinpath("static"))
        app = Quart(__name__, static_folder=src_path)
        env_ambient = os.getenv("AMBIENT_CONFIG")
        ambient = objects_config[env_ambient]
        app.config.from_object(ambient)
        self.init_extensions(app)
        self.init_blueprints(app)

        # Initialize logs module
        from utils.bots_logs import asyncinit_log

        log_file = Path(__file__).parent.resolve().joinpath("logs").joinpath("web.log")
        app.logger = asyncio.run(asyncinit_log(log_file=log_file))

        return app

    def init_blueprints(self, app: Quart) -> None:
        """Register blueprints with the Quart application.

        Args:
            app (Quart): The Quart application instance.

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

    def init_database(self, app: Quart, db: SQLAlchemy) -> None:
        """Initialize the database schema if not already created.

        Args:
            app (Quart): The Quart application instance.
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
