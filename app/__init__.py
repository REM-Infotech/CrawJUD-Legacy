"""Initialize the CrawJUD-Bots app with Quart, Celery, AsyncServer, and extension.

This module creates the Quart app and configures extensions like Celery,
AsyncServer, Quart-Mail, SQLAlchemy, and Talisman.
"""

import asyncio
import platform
import signal
import sys
from datetime import timedelta
from os import environ, getenv
from pathlib import Path
from threading import Thread

import quart_flask_patch  # noqa: F401
import uvicorn
from celery import Celery
from clear import clear
from dotenv_vault import load_dotenv
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from quart import Quart as Quart
from redis_flask import Redis
from socketio import ASGIApp, AsyncRedisManager, AsyncServer

from app.routes import register_routes

valides = [
    getenv("IN_PRODUCTION", None) is None,
    platform.system() == "Windows",
    getenv("DEBUG", "False").lower() == "true",
]

asc = any(valides)

async_mode = "asgi"

load_dotenv()


mail = Mail()
tslm = Talisman()
db = SQLAlchemy()
io = None
app = Quart(__name__)
clean_prompt = False
redis = Redis()

objects_config = {
    "development": "app.config.DevelopmentConfig",
    "production": "app.config.ProductionConfig",
    "testing": "app.config.TestingConfig",
}

clear()
load_dotenv()

values = environ.get
is_init = Path("is_init.txt").resolve()


class AppFactory:
    """Factory to create and configure the ASGIApp and Celery."""

    async def main(self) -> tuple[ASGIApp, Celery]:
        """Run the main application loop."""
        task = asyncio.create_task(self.create_app())
        await task

        return task.result()

    async def create_app(self) -> tuple[ASGIApp, Celery]:
        """Create and configure the ASGIApp and Celery worker.

        Returns:
            tuple: A tuple containing ASGIApp and Celery worker.

        """
        env_ambient = environ["AMBIENT_CONFIG"]
        ambient = objects_config[env_ambient]
        app.config.from_object(ambient)

        async with app.app_context():
            from utils import asyncinit_log as init_log
            from utils import make_celery

            celery = await make_celery(app)
            celery.set_default()
            app.extensions["celery"] = celery

            celery.autodiscover_tasks(["bot", "utils"])

            io = await self.init_extensions(app)
            app.logger = await init_log()
            await self.init_routes(app)
        return ASGIApp(io, app), celery

    async def init_routes(self, app: Quart) -> None:
        """Initialize and register the application routes."""
        async with app.app_context():
            await register_routes(app)

    async def init_extensions(self, app: Quart) -> AsyncServer:
        """Initialize and configure the application extensions."""
        from app.models import (  # noqa: F401
            Servers,
            ThreadBots,
        )
        from utils import check_allowed_origin

        host_redis = getenv("REDIS_HOST")
        pass_redis = getenv("REDIS_PASSWORD")
        port_redis = getenv("REDIS_PORT")

        redis.init_app(app)
        mail.init_app(app)
        db.init_app(app)
        tslm.init_app(
            app,
            content_security_policy=app.config["CSP"],
            session_cookie_http_only=True,
            session_cookie_samesite="Lax",
            strict_transport_security=True,
            strict_transport_security_max_age=timedelta(days=31).max.seconds,
            x_content_type_options=True,
        )
        redis_manager = AsyncRedisManager(url=f"redis://:{pass_redis}@{host_redis}:{port_redis}/8")
        io = AsyncServer(
            async_mode=async_mode,
            cors_allowed_origins=check_allowed_origin,
            client_manager=redis_manager,
            ping_interval=25,
            ping_timeout=10,
        )
        db.create_all()

        if not Servers.query.filter(Servers.name == environ.get("NAMESERVER")).first():  # pragma: no cover
            server = Servers(name=environ.get("NAMESERVER"), address=environ.get("HOSTNAME"), system=platform.system())
            db.session.add(server)
            db.session.commit()

        app.extensions["socketio"] = io

        return io

    @classmethod
    def start_app(cls) -> tuple[ASGIApp, Celery]:  # pragma: no cover
        """Initialize and start the Quart application with AsyncServer.

        Sets up the application context, configures server settings,
        and starts the application using specified parameters.

        Returns:
            tuple: A tuple containing the Quart application and Celery worker.

        """
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.get_event_loop()

        app, celery = loop.run_until_complete(AppFactory().main())
        args_run: dict[str, str | int | bool] = {}
        # app.app_context().push()

        debug = values("DEBUG", "False").lower() == "True"

        port = int(values("PORT", "8000"))

        args_run = {
            "debug": debug,
            "port": port,
            "log_output": True,
            "app": app,
        }

        try:
            if getenv("APPLICATION_APP") != "beat":
                if getenv("APPLICATION_APP") == "quart" and getenv("IN_PRODUCTION", "False") == "True":
                    cls.starter(**args_run)

                elif getenv("APPLICATION_APP") == "worker" and getenv("IN_PRODUCTION", "False") == "False":
                    starter = Thread(target=cls.starter, kwargs=args_run)
                    starter.daemon = True
                    starter.start()

        except (KeyboardInterrupt, TypeError):
            sys.exit(0)

        return app, celery

    @classmethod
    def starter(cls, port: int, log_output: bool, app: Quart, **kwargs: dict[str, any]) -> None:
        """Start the application with the specified parameters.

        Args:
            port (int): The port to listen on.
            log_output (bool): Whether to log output.
            app (Quart): The Quart application instance.
            **kwargs: Additional keyword arguments.

        """
        # Create a WebSocket

        port = kwargs.pop("port", port)
        log_output = kwargs.pop("log_output", log_output)
        app = kwargs.pop("app", app)

        uvicorn.run(
            app,
            host="0.0.0.0",  # noqa: S104 # nosec
            port=port,
        )

    @staticmethod
    def handle_exit(a: any = None, b: any = None) -> None:
        """Handle termination signals and exit the program gracefully."""
        sys.exit(0)


signal.signal(signal.SIGTERM, AppFactory.handle_exit)
signal.signal(signal.SIGINT, AppFactory.handle_exit)
