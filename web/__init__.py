"""Main application module.

This module initializes extensions, blueprints, and the database,
and provides a factory for creating the Quart app.
"""

# Quart imports
# Python Imports
import asyncio
import logging
import os
import subprocess
from datetime import timedelta
from importlib import import_module
from pathlib import Path

import aiofiles
import clear
import quart_flask_patch  # noqa: F401
import uvicorn
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

# APP Imports
from quart import Quart

from web.custom import QuartLoginManager as LoginManager

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

    async def init_extensions(self, app: Quart) -> None:
        """Initialize Quart extensions and middleware.

        Args:
            app (Quart): The Quart application instance.

        """
        db.init_app(app)
        mail.init_app(app)
        login_manager.init_app(app)

        async with app.app_context():
            await self.init_database(app, db)

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

    async def create_app(self) -> Quart:
        """Create and configure the Quart application.

        Returns:
            Quart: The configured Quart application.

        """
        src_path = str(Path(__file__).parent.resolve().joinpath("static"))
        app = Quart(__name__, static_folder=src_path)
        env_ambient = os.getenv("AMBIENT_CONFIG")
        ambient = objects_config[env_ambient]
        app.config.from_object(ambient)
        await self.init_extensions(app)
        await self.init_blueprints(app)

        # Initialize logs module
        from utils.bots_logs import asyncinit_log

        log_file = Path(__file__).cwd().resolve().joinpath("logs").joinpath("web.log")
        app.logger = await asyncinit_log(log_file=log_file)

        return app

    async def init_blueprints(self, app: Quart) -> None:
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

    async def init_database(self, app: Quart, db: SQLAlchemy) -> None:
        """Initialize the database schema if not already created.

        Args:
            app (Quart): The Quart application instance.
            db (SQLAlchemy): The SQLAlchemy database instance.

        """
        from web.models import init_database

        if not Path("is_init.txt").exists():
            async with aiofiles.open("is_init.txt", "w") as f:
                await f.write(f"{await init_database(app, db)}")

        from web.models import Users

        if not db.engine.dialect.has_table(db.engine.connect(), Users.__tablename__):
            async with aiofiles.open("is_init.txt", "w") as f:
                await f.write(f"{await init_database(app, db)}")

    @classmethod
    def construct_app(cls) -> None:
        """Run the Quart application with Uvicorn server."""
        from utils.bots_logs import asyncinit_log_dict

        app = asyncio.run(cls().create_app())
        clear.clear()
        port = int(os.getenv("PORT", 5000))
        hostname = os.getenv(
            "SERVER_HOSTNAME",
            subprocess.run(
                [
                    "powershell",
                    "hostname",
                ],
                capture_output=True,
                text=True,
                check=False,
            ).stdout.strip(),
        )

        log_path = Path(__file__).cwd().resolve().joinpath("logs", "uvicorn_web.log")
        log_path.touch(exist_ok=True)

        log_cfg = asyncio.run(
            asyncinit_log_dict(
                log_path,
                logging.DEBUG,
            )
        )
        # debug = os.getenv("DEBUG", "False").lower() == "true"
        uvicorn.run(
            app,
            host=hostname,
            port=port,
            log_config=log_cfg,
        )
