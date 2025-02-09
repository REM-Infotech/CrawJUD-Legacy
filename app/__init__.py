"""Initialize the CrawJUD-Bots app with Quart, Celery, AsyncServer, and extension.

This module creates the Quart app and configures extensions like Celery,
AsyncServer, Quart-Mail, SQLAlchemy, and Talisman.
"""

import asyncio
import platform
import signal
import subprocess  # noqa: S404, E402 # nosec: B404
import sys
from datetime import timedelta
from os import environ, getenv
from pathlib import Path
from platform import system
from threading import Thread

import quart_flask_patch  # noqa: F401
import uvicorn
from celery import Celery
from clear import clear  # noqa: F401, E402
from dotenv_vault import load_dotenv
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from quart import Quart as Quart
from redis_flask import Redis
from socketio import ASGIApp, AsyncRedisManager, AsyncServer  # noqa: F401
from tqdm import tqdm

from app.routes import register_routes
from utils import asyncinit_log as init_log
from utils import check_allowed_origin, make_celery, version_file

valides = [
    getenv("INTO_DOCKER", None) is None,
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

objects_config = {
    "development": "app.config.DevelopmentConfig",
    "production": "app.config.ProductionConfig",
    "testing": "app.config.TestingConfig",
}

clear()
load_dotenv()

values = environ.get
is_init = Path("is_init.txt").resolve()

from app.models import (  # noqa: E402, F401  # noqa: E402, F401
    Servers,
    ThreadBots,
)


class AppFactory:
    """Factory to create and configure the ASGIApp and Celery."""

    async def init_blueprints(self, app: Quart) -> None:
        """Register blueprints with the Flask application.

        Args:
            app (Flask): The Flask application instance.

        """
        from app.routes.auth import auth
        from app.routes.bot import bot
        from app.routes.config import admin, supersu, usr
        from app.routes.credentials import cred
        from app.routes.dashboard import dash
        from app.routes.execution import exe
        from app.routes.logs import logsbot
        from app.routes.webhook import wh

        listBlueprints = [bot, auth, logsbot, exe, dash, cred, admin, supersu, usr, wh]  # noqa: N806

        for bp in listBlueprints:
            app.register_blueprint(bp)

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
        # for key, value in environ.items():
        #     print(f"{key}={value}")  # noqa: T201

        env_ambient = environ["AMBIENT_CONFIG"]
        ambient = objects_config[env_ambient]
        app.config.from_object(ambient)

        celery = make_celery(app)
        celery.set_default()
        app.extensions["celery"] = celery

        celery.autodiscover_tasks(["bot"])

        async with app.app_context():
            await asyncio.create_task(self.init_database(app))
            await asyncio.create_task(self.init_mail(app))
            await asyncio.create_task(self.init_redis(app))
            await asyncio.create_task(self.init_talisman(app))
            io = await asyncio.create_task(self.init_socket(app))
            app.logger = await asyncio.create_task(init_log())
            await asyncio.create_task(self.init_routes(app))
        return ASGIApp(io, app), celery

    async def init_routes(self, app: Quart) -> None:
        """Initialize and register the application routes."""
        await register_routes(app)

    async def init_talisman(self, app: Quart) -> Talisman:
        """Initialize Talisman for security headers.

        Args:
            app (Quart): The Quart application.

        Returns:
            Talisman: The Talisman instance.

        """
        tslm.init_app(
            app,
            content_security_policy=app.config["CSP"],
            session_cookie_http_only=True,
            session_cookie_samesite="Lax",
            strict_transport_security=True,
            strict_transport_security_max_age=timedelta(days=31).max.seconds,
            x_content_type_options=True,
        )
        return tslm

    async def init_socket(self, app: Quart) -> AsyncServer:
        """Initialize the AsyncServer instance.

        Args:
            app (Quart): The Quart application.

        Returns:
            AsyncServer: The initialized AsyncServer instance.

        """
        host_redis = getenv("REDIS_HOST")
        pass_redis = getenv("REDIS_PASSWORD")
        port_redis = getenv("REDIS_PORT")
        r_mg = AsyncRedisManager(url=f"redis://:{pass_redis}@{host_redis}:{port_redis}/8")
        io = AsyncServer(
            async_mode=async_mode,
            cors_allowed_origins=check_allowed_origin,
            client_manager=r_mg,
            ping_interval=25,
            ping_timeout=10,
        )

        app.extensions["socketio"] = io

        return io

    async def init_mail(self, app: Quart) -> None:
        """Initialize the Quart-Mail extension."""
        mail.init_app(app)

    async def init_redis(self, app: Quart) -> Redis:
        """Initialize the Redis extension.

        Args:
            app (Quart): The Quart application.

        Returns:
            Redis: The Redis instance.

        """
        global redis

        redis = Redis(app)
        return redis

    async def init_database(self, app: Quart) -> SQLAlchemy:
        """Initialize the database and create tables if they do not exist.

        Args:
            app (Quart): The Quart application.

        Returns:
            SQLAlchemy: The database instance.

        """
        import platform

        global db

        async with app.app_context():
            db.init_app(app)

            if environ["HOSTNAME"] == "betatest1.rhsolut.com.br":
                db.drop_all()

            db.create_all()

            NAMESERVER = environ.get("NAMESERVER")  # noqa: N806
            HOST = environ.get("HOSTNAME")  # noqa: N806

            if not Servers.query.filter(Servers.name == NAMESERVER).first():
                server = Servers(name=NAMESERVER, address=HOST, system=platform.system())
                db.session.add(server)
                db.session.commit()

        return db

    @classmethod
    def start_app(cls) -> tuple[Quart, Celery]:
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

        hostname = values("SERVER_HOSTNAME", "127.0.0.1")

        # unsafe_werkzeug = getenv("INTO_DOCKER", None) is None or (getenv("DEBUG", "False").lower() == "true")
        port = int(values("PORT", "8000"))
        version_file()
        if system().lower() == "linux":
            AppFactory.start_vnc()

        args_run = {
            "hostname": hostname,
            "debug": debug,
            "port": port,
            "log_output": True,
            "app": app,
        }

        try:
            if getenv("APPLICATION_APP") != "beat":
                if getenv("INTO_DOCKER", "False") == "False" and getenv("APPLICATION_APP") == "worker":
                    starter = Thread(target=cls.starter, kwargs=args_run)
                    starter.daemon = True
                    starter.start()

                if getenv("APPLICATION_APP") == "quart" and getenv("INTO_DOCKER", "False") == "True":
                    cls.starter(**args_run)

        except (KeyboardInterrupt, TypeError):
            if system().lower() == "linux":
                try:
                    subprocess.run(["tightvncserver", "-kill", ":99"], check=False)  # noqa: S603, S607 # nosec: B603, B607

                except Exception:
                    # err = traceback.format_exc()
                    # app.logger.exception(err)
                    ...

            sys.exit(0)

        return app, celery

    @classmethod
    def starter(cls, hostname: str, port: int, log_output: bool, app: Quart, **kwargs: dict[str, any]) -> None:
        """Start the application with the specified parameters.

        Args:
            hostname (str): The hostname to listen on.
            port (int): The port to listen on.
            log_output (bool): Whether to log output.
            app (Quart): The Quart application instance.
            **kwargs: Additional keyword arguments.

        """
        # Create a WebSocket

        hostname = kwargs.pop("hostname", hostname)
        port = kwargs.pop("port", port)
        log_output = kwargs.pop("log_output", log_output)
        app = kwargs.pop("app", app)

        uvicorn.run(app, host=hostname, port=port)

    @staticmethod
    def handle_exit(a: any = None, b: any = None) -> None:
        """Handle termination signals and exit the program gracefully."""
        sys.exit(0)

    @staticmethod
    def start_vnc() -> None:
        """Start the TightVNC server with specified parameters."""
        try:
            # Executa o comando com verificação de erro
            subprocess.run(  # noqa: S603 # nosec: B607, B603
                [  # noqa: S607
                    "tightvncserver",
                    ":99",
                    "-geometry",
                    "1600x900",
                    "-depth",
                    "24",
                    "-rfbport",
                    "5999",
                ],
                check=True,  # Lança exceção se o comando falhar
            )
            tqdm.write.info("VNC Server started successfully.")
        except Exception:
            ...


signal.signal(signal.SIGTERM, AppFactory.handle_exit)
signal.signal(signal.SIGINT, AppFactory.handle_exit)
