from datetime import timedelta
from os import getenv
from pathlib import Path

from celery import Celery
from clear import clear
from os import environ
from dotenv_vault import load_dotenv
from flask import Flask
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from redis_flask import Redis

from .utils import check_allowed_origin, make_celery

import platform

async_mode = (
    str("threading")
    if (getenv("INTO_DOCKER", None) is None or platform.system() == "Windows")
    or (getenv("DEBUG", "False").lower() == "true")
    else str("eventlet")
)

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

    def create_app(self) -> tuple[Flask, SocketIO, Celery]:

        global app

        # redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True, password=)

        env_ambient = environ["AMBIENT_CONFIG"]
        ambient = objects_config[env_ambient]
        app.config.from_object(ambient)

        celery = make_celery(app)
        celery.set_default()
        app.extensions["celery"] = celery

        celery.autodiscover_tasks(["bot"])

        if app.testing is False:  # pragma: no cover

            with app.app_context():
                self.init_database(app)
                self.init_mail(app)
                self.init_redis(app)

                self.init_talisman(app)
                io = self.init_socket(app)
                self.init_routes(app)

                return app, io, celery

        return app, io, celery

    def init_routes(self, app: Flask) -> None:

        from app.routes import register_routes

        register_routes(app)

    def init_talisman(self, app: Flask) -> Talisman:  # pragma: no cover

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
        global io

        host_redis = getenv("REDIS_HOST")
        pass_redis = getenv("REDIS_PASSWORD")
        port_redis = getenv("REDIS_PORT")

        io = SocketIO(
            async_mode="threading",
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

        mail.init_app(app)

    def init_redis(self, app: Flask) -> Redis:

        global redis

        redis = Redis(app)
        return redis

    def init_database(self, app: Flask) -> SQLAlchemy:

        import platform

        global db
        with app.app_context():

            db.init_app(app)

            if not Path("is_init.txt").exists():

                with open("is_init.txt", "w") as f:
                    db.create_all()
                    f.write("True")

            from app.models import Servers, ThreadBots

            if not db.engine.dialect.has_table(
                db.engine.connect(), ThreadBots.__tablename__
            ):
                with open("is_init.txt", "w") as f:

                    db.create_all()
                    f.write("True")

            NAMESERVER = environ.get("NAMESERVER")
            HOST = environ.get("HOSTNAME")

            if not Servers.query.filter(Servers.name == NAMESERVER).first():

                server = Servers(
                    name=NAMESERVER, address=HOST, system=platform.system()
                )
                db.session.add(server)
                db.session.commit()

            return db


create_app = AppFactory().create_app  # pragma: no cover
