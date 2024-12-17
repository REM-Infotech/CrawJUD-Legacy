import os
import re
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

from dotenv import dotenv_values


class Configurator:

    env_file = ".env"

    def __init__(self):

        debug_flag = Path(".debug").exists()
        if debug_flag:
            self.env_file = ".testing"

    def get_configurator(self) -> dict:  # pragma: no cover

        class ConfigObject:

            values = dotenv_values(self.env_file)
            login_db = values.get("LOGIN")
            passwd_db = values.get("PASSWORD")
            host_db = values.get("HOST")
            database_name = values.get("DATABASE")

            os.makedirs("Archives", exist_ok=True)

            # FLASK-MAIL CONFIG
            MAIL_SERVER = values["MAIL_SERVER"]
            MAIL_PORT = int(values["MAIL_PORT"])
            MAIL_USE_TLS = False
            MAIL_USE_SSL = False
            MAIL_USERNAME = values["MAIL_USERNAME"]
            MAIL_PASSWORD = values["MAIL_PASSWORD"]
            MAIL_DEFAULT_SENDER = values["MAIL_DEFAULT_SENDER"]

            # SqlAlchemy config
            SQLALCHEMY_POOL_SIZE = 30  # Número de conexões na pool
            SQLALCHEMY_MAX_OVERFLOW = 10  # Número de conexões extras além da pool_size
            SQLALCHEMY_POOL_TIMEOUT = 30  # Tempo de espera para obter uma conexão
            SQLALCHEMY_POOL_RECYCLE = (
                1800  # Tempo (em segundos) para reciclar as conexões ociosas
            )
            SQLALCHEMY_POOL_PRE_PING = (
                True  # Verificar a saúde da conexão antes de usá-la
            )

            SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{login_db}:{passwd_db}@{host_db}/{database_name}"
            SQLALCHEMY_BINDS = {"cachelogs": "sqlite:///cachelogs.db"}
            SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
            SQLALCHEMY_TRACK_MODIFICATIONS = False

            # FLASK CONFIG
            PREFERRED_URL_SCHEME = "https"
            SESSION_COOKIE_HTTPONLY = False
            SESSION_COOKIE_SECURE = True
            PERMANENT_SESSION_LIFETIME = timedelta(days=31).max.seconds
            SECRET_KEY = str(uuid4())

            REDIS_HOST = values.get("REDIS_HOST")
            REDIS_PORT = int(values.get("REDIS_PORT"))
            REDIS_DB = int(values.get("REDIS_DB"))
            REDIS_PASSWORD = values.get("REDIS_PASSWORD")

            WEBHOOK_SECRET = values.get("WEBHOOK_SECRET")

        return ConfigObject


def csp() -> dict[str]:  # pragma: no cover

    from app.models import Servers

    srvs = Servers.query.all()
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

    return csp_vars


def check_allowed_origin(origin="https://google.com"):  # pragma: no cover
    allowed_origins = [
        r"https:\/\/.*\.nicholas\.dev\.br",
        r"https:\/\/.*\.robotz\.dev",
        r"https:\/\/.*\.rhsolutions\.info",
        r"https:\/\/.*\.rhsolut\.com\.br",
    ]
    if not origin:
        origin = f'https://{dotenv_values().get("HOSTNAME")}'

    for orig in allowed_origins:
        pattern = orig
        matchs = re.match(pattern, origin)
        if matchs:
            return True

    return False
