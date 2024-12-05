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

    def create_test_app(self) -> tuple[Flask, SocketIO]:

        global app

        # redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True, password=)
        src_path = os.path.join(pathlib.Path(__file__).cwd(), "static")
        app = Flask(__name__, static_folder=src_path)
        app.config.from_object(default_config)

        io = self.init_extensions(app)

        import_module("app.routes", __name__)
        import_module("app.handling", __name__)

        return app, io, db

    def create_app(self) -> tuple[Flask, SocketIO]:

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
            db = SQLAlchemy()
            db.init_app(app)
            mail = Mail(app)

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


class AppTestFactory:

    csp_ = {}

    @property
    def csp(self):
        return self.csp_

    @csp.setter
    def csp(self, new_csp: dict):
        self.csp_ = new_csp

    def set_csp(self, srvs):

        csp_vars = {
            "default-src": ["'self'"],
            "script-src": [
                "'self'",
                "https://cdn.jsdelivr.net",
                "https://cdnjs.cloudflare.com",
                "https://cdn.datatables.net",
                "https://unpkg.com",
                "https://code.jquery.com",
                "https://use.fontawesome.com",
                "",
                "'unsafe-inline'",
            ],
            "style-src": [
                "'self'",
                "https://cdn.jsdelivr.net",
                "https://cdnjs.cloudflare.com",
                "https://cdn.datatables.net",
                "https://unpkg.com",
                "https://github.com",
                "https://avatars.githubusercontent.com",
                "'unsafe-inline'",
            ],
            "img-src": [
                "'self'",
                "data:",
                "https://cdn.jsdelivr.net",
                "https://cdnjs.cloudflare.com",
                "https://cdn.datatables.net",
                "https://unpkg.com",
                "https://cdn-icons-png.flaticon.com",
                "https://github.com",
                "https://domain.cliente.com",
                "https://avatars.githubusercontent.com",
            ],
            "connect-src": [
                "'self'",
                "https://cdn.jsdelivr.net",
                "https://cdnjs.cloudflare.com",
                "https://cdn.datatables.net",
                "https://github.com",
                "https://unpkg.com",
                "https://avatars.githubusercontent.com",
            ],
            "frame-src": [
                "'self'",
                "https://domain.cliente.com",
                "https://github.com",
                "https://avatars.githubusercontent.com",
            ],
        }
        if srvs:
            for srv in srvs:
                csp_vars.get("connect-src").append(f"https://{srv.address}")
                csp_vars.get("connect-src").append(f"wss://{srv.address}")

        self.csp = csp_vars

    def create_app(self) -> tuple[Flask, SocketIO, SQLAlchemy]:

        global app

        # redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True, password=)
        src_path = os.path.join(pathlib.Path(__file__).cwd(), "static")
        app = Flask(__name__, static_folder=src_path)
        app.config.from_object(default_config)

        io, db = self.init_extensions(app)

        import_module("app.routes", __name__)
        import_module("app.handling", __name__)

        return app, io, db

    def init_extensions(self, app: Flask) -> tuple[SocketIO, SQLAlchemy]:

        with app.app_context():
            global db, mail, io, redis

            redis = Redis(app)
            db = SQLAlchemy()
            db.init_app(app)
            mail = Mail(app)

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
                    self.init_database(db)
                    f.write("True")

            from app.models import Users

            if not db.engine.dialect.has_table(
                db.engine.connect(), Users.__tablename__
            ):
                with open("is_init.txt", "w") as f:
                    self.init_database(db)
                    f.write("True")

            CustomTalisman(
                app,
                content_security_policy=self.csp,
                session_cookie_http_only=True,
                session_cookie_samesite="Lax",
                strict_transport_security=True,
                strict_transport_security_max_age=timedelta(days=31).max.seconds,
                x_content_type_options=True,
            )
        return io, db

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

        servers = Servers.query.all()
        self.set_csp(servers)


create_app = AppFactory().create_app
create_test_app = AppTestFactory().create_app
