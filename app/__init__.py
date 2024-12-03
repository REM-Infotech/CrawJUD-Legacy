# Flask imports
# Python Imports
import os
import pathlib
import re
from datetime import timedelta
from importlib import import_module
from pathlib import Path

from dotenv import dotenv_values
from flask import Flask
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

from app import default_config

# APP Imports
from configs import csp
from redis_flask import Redis

db = None
mail = None
io = None
app = None


clean_prompt = False

allowed_origins = [
    r"https:\/\/.*\.nicholas\.dev\.br",
    r"https:\/\/.*\.robotz\.dev",
    r"https:\/\/.*\.rhsolutions\.info",
    r"https:\/\/.*\.rhsolut\.com\.br",
]


def check_allowed_origin(origin="https://google.com"):

    if not origin:
        origin = f'https://{dotenv_values().get("HOSTNAME")}'

    for orig in allowed_origins:
        pattern = orig
        matchs = re.match(pattern, origin)
        if matchs:
            return True

    return False


class CustomTalisman(Talisman):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_headers(self, response):
        super().set_headers(response)


class AppFactory:

    def create_app(self) -> Flask:

        global app

        # redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True, password=)
        src_path = os.path.join(pathlib.Path(__file__).cwd(), "static")
        app = Flask(__name__, static_folder=src_path)
        app.config.from_object(default_config)

        io = self.init_extensions(app)

        import_module("app.routes", __name__)
        import_module("app.handling", __name__)

        return app, io

    def init_extensions(self, app: Flask) -> SocketIO:

        with app.app_context():
            global db, mail, io, redis

            redis = Redis(app)
            db = SQLAlchemy(app)
            mail = Mail(app)

            # redis_url = "redis://:ed67AwFki0tM@195.35.43.119:6379"
            io = SocketIO(app, async_mode="eventlet")

            mail.init_app(app)
            io.init_app(
                app,
                cors_allowed_origins=check_allowed_origin,
                ping_interval=25,
                ping_timeout=10,
            )

            if not Path("is_init.txt").exists():

                with open("is_init.txt", "w") as f:
                    f.write("True")

                self.init_database(db)

            CustomTalisman(
                app,
                content_security_policy=csp(),
                session_cookie_http_only=True,
                session_cookie_samesite="Lax",
                strict_transport_security=True,
                strict_transport_security_max_age=timedelta(days=31).max.seconds,
                x_content_type_options=True,
            )
        return io

    def init_database(self, db: SQLAlchemy):

        import platform

        from .models import Servers

        values = dotenv_values()
        db.create_all()

        NAMESERVER = values.get("NAMESERVER")
        HOST = values.get("HOSTNAME")

        if not Servers.query.filter(Servers.name == NAMESERVER).first():

            server = Servers(name=NAMESERVER, address=HOST, system=platform.system())
            db.session.add(server)
            db.session.commit()


create_app = AppFactory().create_app
