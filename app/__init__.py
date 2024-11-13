# Flask imports
from flask import Flask
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

# Python Imports
import os
import re

from pathlib import Path
from datetime import timedelta
from dotenv import dotenv_values
from importlib import import_module

# APP Imports
from configs import csp
from app import default_config

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


def check_allowed_origin(origin: str = "https://google.com"):

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
        src_path = os.path.join(os.getcwd(), "static")
        app = Flask(__name__, static_folder=src_path)
        app.config.from_object(default_config)

        self.init_extensions(app)

        import_module("app.routes", __name__)
        import_module("app.handling", __name__)

        return app

    def init_extensions(self, app: Flask):

        with app.app_context():
            global db, mail, io
            db = SQLAlchemy()
            mail = Mail()
            io = SocketIO(app)

            mail.init_app(app)
            db.init_app(app)
            io.init_app(
                app,
                cors_allowed_origins=check_allowed_origin,
                async_mode="gevent",
                ping_interval=25,
                ping_timeout=10,
            )

            CustomTalisman(
                app,
                content_security_policy=csp(),
                session_cookie_http_only=True,
                session_cookie_samesite="Lax",
                strict_transport_security=True,
                strict_transport_security_max_age=timedelta(days=31).max.seconds,
                x_content_type_options=True,
            )

            if not Path("is_init.txt").exists():

                with open("is_init.txt", "w") as f:
                    f.write("True")

                self.init_database(db)

    def init_database(self, db: SQLAlchemy):

        from .models import Servers
        import platform

        values = dotenv_values()
        db.create_all()

        NAMESERVER = values.get("NAMESERVER")
        HOST = values.get("HOSTNAME")

        if not Servers.query.filter(Servers.name == NAMESERVER).first():

            server = Servers(name=NAMESERVER, address=HOST, system=platform.system())
            db.session.add(server)
            db.session.commit()


create_app = AppFactory().create_app
