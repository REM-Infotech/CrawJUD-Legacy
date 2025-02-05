"""Initialize the CrawJUD-Bots app with Flask, Celery, SocketIO, and extension.

This module creates the Flask app and configures extensions like Celery,
SocketIO, Flask-Mail, SQLAlchemy, and Talisman.
"""

import platform
from datetime import timedelta
from os import environ, getenv
from pathlib import Path

from celery import Celery
from clear import clear
from dotenv_vault import load_dotenv
from flask import Flask
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from redis_flask import Redis

from .utils import check_allowed_origin, init_log, make_celery

valides = [
    getenv("INTO_DOCKER", None) is None,
    platform.system() == "Windows",
    getenv("DEBUG", "False").lower() == "true",
]

asc = any(valides)

async_mode = str("threading") if asc is True else str("eventlet")

load_dotenv()

mail = Mail()
tslm = Talisman()
db = SQLAlchemy()

io = None
app = None
app = Flask(__name__)
clean_prompt = False

objects_config = {
    "development": "app.config.DevelopmentConfig",
    "production": "app.config.ProductionConfig",
    "testing": "app.config.TestingConfig",
}

clear()
load_dotenv()


class AppFactory:
    """Factory to create and configure the Flask app, SocketIO, and Celery."""

    def create_app(self) -> tuple[Flask, SocketIO, Celery]:
        """Create and configure the Flask app, SocketIO, and Celery worker.

        Returns:
            tuple: A tuple containing Flask app, SocketIO, and Celery worker.

        """
        global app

        # Temporarily disable Redis client
        # redis_client = redis.Redis(host='localhost', port=6379,
        # decode_responses=True, password=)

        env_ambient = environ["AMBIENT_CONFIG"]
        ambient = objects_config[env_ambient]
        app.config.from_object(ambient)

        celery = make_celery(app)
        celery.set_default()
        app.extensions["celery"] = celery

        celery.autodiscover_tasks(["bot"])

        if not app.testing:  # pragma: no cover
            with app.app_context():
                self.init_database(app)
                self.init_mail(app)
                self.init_redis(app)

                self.init_talisman(app)
                io = self.init_socket(app)
                self.init_routes(app)

                return app, io, celery

        app.logger = init_log()
        return app, io, celery

    def init_routes(self, app: Flask) -> None:
        """Initialize and register the application routes."""
        from app.routes import register_routes

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

        io = SocketIO(
            async_mode=async_mode,
            message_queue=f"redis://:{pass_redis}@{host_redis}:{port_redis}/9",
        )

        io.init_app(
            app,
            cors_allowed_origins=check_allowed_origin,
            ping_interval=25,
            ping_timeout=10,
        )

        return io

    def init_mail(self, app) -> None:
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


create_app = AppFactory().create_app  # pragma: no cover
