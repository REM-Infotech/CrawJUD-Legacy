"""Initialize the CrawJUD-Bots app with Flask, Celery, SocketIO, and extension.

This module creates the Flask app and configures extensions like Celery,
SocketIO, Flask-Mail, SQLAlchemy, and Talisman.
"""

from gevent import monkey

monkey.patch_all()

import platform  # noqa: E402
import signal  # noqa: E402
import subprocess  # noqa: S404, E402 # nosec: B404
import sys  # noqa: E402
from datetime import timedelta  # noqa: E402
from os import environ, getenv  # noqa: E402
from pathlib import Path  # noqa: E402
from platform import system  # noqa: E402
from threading import Thread  # noqa: E402

from celery import Celery  # noqa: E402
from clear import clear  # noqa: F401, E402
from dotenv_vault import load_dotenv  # noqa: E402
from flask import Flask  # noqa: E402
from flask_mail import Mail  # noqa: E402
from flask_socketio import SocketIO  # noqa: E402
from flask_sqlalchemy import SQLAlchemy  # noqa: E402
from flask_talisman import Talisman  # noqa: E402
from gevent.pywsgi import WSGIServer  # noqa: E402
from geventwebsocket.handler import WebSocketHandler  # noqa: E402
from redis_flask import Redis  # noqa: E402
from tqdm import tqdm  # noqa: E402

from app.routes import register_routes  # noqa: E402
from git_py import version_file  # noqa: E402

from .utils import check_allowed_origin, init_log, make_celery  # noqa: E402

valides = [
    getenv("INTO_DOCKER", None) is None,
    platform.system() == "Windows",
    getenv("DEBUG", "False").lower() == "true",
]

asc = any(valides)

async_mode = "gevent"

load_dotenv()

mail = Mail()
tslm = Talisman()
db = SQLAlchemy()

io = SocketIO(async_mode=async_mode)
app = Flask(__name__)
clean_prompt = False

objects_config = {
    "development": "app.config.DevelopmentConfig",
    "production": "app.config.ProductionConfig",
    "testing": "app.config.TestingConfig",
}

# clear()
load_dotenv()

values = environ.get


class AppFactory:
    """Factory to create and configure the Flask app, SocketIO, and Celery."""

    def create_app(self) -> tuple[Flask, SocketIO, Celery]:
        """Create and configure the Flask app, SocketIO, and Celery worker.

        Returns:
            tuple: A tuple containing Flask app, SocketIO, and Celery worker.

        """
        env_ambient = environ["AMBIENT_CONFIG"]
        ambient = objects_config[env_ambient]
        app.config.from_object(ambient)

        celery = make_celery(app)
        celery.set_default()
        app.extensions["celery"] = celery

        celery.autodiscover_tasks(["bot"])

        if not app.testing:
            with app.app_context():
                self.init_database(app)
                self.init_mail(app)
                self.init_redis(app)

                self.init_talisman(app)
                io = self.init_socket(app)
                self.init_routes(app)
                app.logger = init_log()
                return app, io, celery

        app.logger = init_log()
        return app, io, celery

    def init_routes(self, app: Flask) -> None:
        """Initialize and register the application routes."""
        register_routes(app)

    def init_talisman(self, app: Flask) -> Talisman:
        """Initialize Talisman for security headers.

        Args:
            app (Flask): The Flask application.

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

    def init_socket(self, app: Flask) -> SocketIO:
        """Initialize the SocketIO instance.

        Args:
            app (Flask): The Flask application.

        Returns:
            SocketIO: The initialized SocketIO instance.

        """
        global io

        host_redis = getenv("REDIS_HOST")
        pass_redis = getenv("REDIS_PASSWORD")
        port_redis = getenv("REDIS_PORT")

        io.init_app(
            app,
            cors_allowed_origins=check_allowed_origin,
            ping_interval=25,
            ping_timeout=10,
            message_queue=f"redis://:{pass_redis}@{host_redis}:{port_redis}/8",
        )

        return io

    def init_mail(self, app: Flask) -> None:
        """Initialize the Flask-Mail extension."""
        mail.init_app(app)

    def init_redis(self, app: Flask) -> Redis:
        """Initialize the Redis extension.

        Args:
            app (Flask): The Flask application.

        Returns:
            Redis: The Redis instance.

        """
        global redis

        redis = Redis(app)
        return redis

    def init_database(self, app: Flask) -> SQLAlchemy:
        """Initialize the database and create tables if they do not exist.

        Args:
            app (Flask): The Flask application.

        Returns:
            SQLAlchemy: The database instance.

        """
        import platform

        global db
        with app.app_context():
            db.init_app(app)

            if not Path("is_init.txt").exists():
                with open("is_init.txt", "w") as f:
                    db.create_all()
                    f.write("True")

            from app.models import Servers, ThreadBots

            if not db.engine.dialect.has_table(db.engine.connect(), ThreadBots.__tablename__):
                with open("is_init.txt", "w") as f:
                    db.create_all()
                    f.write("True")

            NAMESERVER = environ.get("NAMESERVER")  # noqa: N806
            HOST = environ.get("HOSTNAME")  # noqa: N806

            if not Servers.query.filter(Servers.name == NAMESERVER).first():
                server = Servers(name=NAMESERVER, address=HOST, system=platform.system())
                db.session.add(server)
                db.session.commit()

            return db

    @classmethod
    def start_app(cls) -> tuple[Flask, Celery]:
        """Initialize and start the Flask application with SocketIO.

        Sets up the application context, configures server settings,
        and starts the application using specified parameters.

        """
        app, _, celery = cls().create_app()

        args_run: dict[str, str | int | bool] = {}
        app.app_context().push()

        debug = values("DEBUG", "False").lower() == "True"

        hostname = values("SERVER_HOSTNAME", "127.0.0.1") if getenv("INTO_DOCKER", None) else "127.0.0.1"

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
            starter = Thread(target=cls.starter, kwargs=args_run)
            starter.daemon = True
            starter.start()

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
    def starter(cls, hostname: str, port: int, log_output: bool, app: Flask, **kwargs: dict[str, any]) -> None:
        """Start the application with the specified parameters.

        Args:
            hostname (str): The hostname to listen on.
            port (int): The port to listen on.
            log_output (bool): Whether to log output.
            app (Flask): The Flask application instance.
            **kwargs: Additional keyword arguments.

        """
        # Create a WebSocket

        hostname = kwargs.pop("hostname", hostname)
        port = kwargs.pop("port", port)
        log_output = kwargs.pop("log_output", log_output)
        app = kwargs.pop("app", app)

        wsgi = WSGIServer((hostname, port), app, handler_class=WebSocketHandler, log=app.logger, error_log=app.logger)

        wsgi.serve_forever()

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


app, celery = AppFactory.start_app()

signal.signal(signal.SIGTERM, AppFactory.handle_exit)
signal.signal(signal.SIGINT, AppFactory.handle_exit)
