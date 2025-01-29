import secrets
from datetime import timedelta
from os import environ
from pathlib import Path
from typing import Dict, List, Type

from dotenv_vault import load_dotenv

load_dotenv()


class Config(object):
    DEBUG: Type[bool] = False
    TESTING: Type[bool] = False
    SECRET_KEY: Type[str] = secrets.token_hex()
    TEMPLATES_AUTO_RELOAD: Type[bool] = False

    # FLASK-MAIL CONFIG
    MAIL_SERVER: Type[str] = ""
    MAIL_PORT: Type[int] = 587
    MAIL_USE_TLS: Type[bool] = False
    MAIL_USE_SSL: Type[bool] = False
    MAIL_USERNAME: Type[str] = ""
    MAIL_PASSWORD: Type[str] = ""
    MAIL_DEFAULT_SENDER: Type[str] = ""

    # SQLALCHEMY CONFIG
    SQLALCHEMY_POOL_SIZE: Type[int] = 30  # Número de conexões na pool

    # Número de conexões extras além da pool_size
    SQLALCHEMY_MAX_OVERFLOW: Type[int] = 10

    # Tempo de espera para obter uma conexão
    SQLALCHEMY_POOL_TIMEOUT: Type[int] = 30

    # Tempo (em segundos) para reciclar as conexões ociosas
    SQLALCHEMY_POOL_RECYCLE: Type[int] = 1800

    # Verificar a saúde da conexão antes de usá-la
    SQLALCHEMY_POOL_PRE_PING: Type[bool] = True

    SQLALCHEMY_BINDS: Dict[str, str] = {"cachelogs": "sqlite:///cachelogs.db"}
    SQLALCHEMY_DATABASE_URI: Type[str] = "sqlite:///local.db"
    SQLALCHEMY_ENGINE_OPTIONS: Dict[str, str | bool] = {"pool_pre_ping": True}
    SQLALCHEMY_TRACK_MODIFICATIONS: Type[bool] = False

    # FLASK CONFIG
    PREFERRED_URL_SCHEME: Type[str] = "https"
    SESSION_COOKIE_HTTPONLY: Type[bool] = False
    SESSION_COOKIE_SECURE: Type[bool] = True
    PERMANENT_SESSION_LIFETIME: Type[int] = timedelta(days=31).max.seconds

    TEMP_PATH: Type[Path] = Path(__file__).cwd().resolve().joinpath("temp")
    ARCHIVES: Type[Path] = Path(__file__).cwd().resolve().joinpath("Archives")
    TEMP_PATH.mkdir(exist_ok=True)
    ARCHIVES.mkdir(exist_ok=True)

    WEBHOOK_SECRET: Type[str] = ""

    REDIS_HOST: Type[str] = ""
    REDIS_PORT: Type[int] = 6379
    REDIS_DB: Type[str] = ""
    REDIS_PASSWORD: Type[str] = ""

    CSP: Dict[str, str | List[str] | List[List[str]]] = {
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
            "https://cdn-icons-png.freepik.com",
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


class ProductionConfig(Config):
    try:
        env = environ

        # Flask-mail config
        MAIL_SERVER = env["MAIL_SERVER"]
        MAIL_PORT = int(env["MAIL_PORT"])
        MAIL_USE_TLS = env["MAIL_USE_TLS"] in ["True", "true", "TRUE"]
        MAIL_USE_SSL = env["MAIL_USE_SSL"] in ["True", "true", "TRUE"]
        MAIL_USERNAME = env["MAIL_USERNAME"]
        MAIL_PASSWORD = env["MAIL_PASSWORD"]
        MAIL_DEFAULT_SENDER = env["MAIL_DEFAULT_SENDER"]

        # SQLALCHEMY CONFIG
        SQLALCHEMY_DATABASE_URI = "".join(
            [
                str(env["DATABASE_CONNECTOR"]),
                "://",
                str(env["DATABASE_USER"]),
                ":",
                str(env["DATABASE_PASSWORD"]),
                "@",
                str(env["DATABASE_HOST"]),
                ":",
                str(env["DATABASE_PORT"]),
                "/",
                str(env["DATABASE_SCHEMA"]),
            ]
        )

        REDIS_HOST = env["REDIS_HOST"]
        REDIS_PORT = env["REDIS_PORT"]
        REDIS_DB = int(env["REDIS_DB"])
        REDIS_PASSWORD = env["REDIS_PASSWORD"]

        WEBHOOK_SECRET = env["WEBHOOK_SECRET"]

        CELERY: Dict[str, str | bool] = {
            "broker_url": f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/6",
            "result_backend": f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/7",
            "task_ignore_result": True,
            "broker_connection_retry_on_startup": True,
            "timezone": "America/Sao_Paulo",
        }

    except Exception as e:
        raise e


class DevelopmentConfig(Config):
    try:
        env = environ

        # Flask-mail config

        if env.get("MAIL_SERVER"):
            MAIL_SERVER = env["MAIL_SERVER"]
            MAIL_PORT = int(env["MAIL_PORT"])
            MAIL_USE_TLS = env["MAIL_USE_TLS"] in ["True", "true", "TRUE"]
            MAIL_USE_SSL = env["MAIL_USE_SSL"] in ["True", "true", "TRUE"]
            MAIL_USERNAME = env["MAIL_USERNAME"]
            MAIL_PASSWORD = env["MAIL_PASSWORD"]
            MAIL_DEFAULT_SENDER = env["MAIL_DEFAULT_SENDER"]

        # SQLALCHEMY CONFIG

        if env.get("DATABASE_HOST"):
            SQLALCHEMY_DATABASE_URI = "".join(
                [
                    str(env["DATABASE_CONNECTOR"]),
                    "://",
                    str(env["DATABASE_USER"]),
                    ":",
                    str(env["DATABASE_PASSWORD"]),
                    "@",
                    str(env["DATABASE_HOST"]),
                    ":",
                    str(env["DATABASE_PORT"]),
                    "/",
                    str(env["DATABASE_SCHEMA"]),
                ]
            )

        REDIS_HOST = env["REDIS_HOST"]
        REDIS_PORT = env["REDIS_PORT"]
        REDIS_DB = int(env["REDIS_DB"])
        REDIS_PASSWORD = env["REDIS_PASSWORD"]

        WEBHOOK_SECRET = env["WEBHOOK_SECRET"]

        CELERY: Dict[str, str | bool] = {
            "broker_url": f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/6",
            "result_backend": f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/7",
            "task_ignore_result": True,
            "broker_connection_retry_on_startup": True,
            "timezone": "America/Sao_Paulo",
        }

    except Exception as e:
        raise e


class TestingConfig(Config):
    try:
        TESTTING = True
        env = environ

        # Flask-mail config

        if env.get("MAIL_SERVER"):
            MAIL_SERVER = env["MAIL_SERVER"]
            MAIL_PORT = int(env["MAIL_PORT"])
            MAIL_USE_TLS = env["MAIL_USE_TLS"] in ["True", "true", "TRUE"]
            MAIL_USE_SSL = env["MAIL_USE_SSL"] in ["True", "true", "TRUE"]
            MAIL_USERNAME = env["MAIL_USERNAME"]
            MAIL_PASSWORD = env["MAIL_PASSWORD"]
            MAIL_DEFAULT_SENDER = env["MAIL_DEFAULT_SENDER"]

        # SQLALCHEMY CONFIG

        if env.get("DATABASE_HOST"):
            SQLALCHEMY_DATABASE_URI = "".join(
                [
                    str(env["DATABASE_CONNECTOR"]),
                    "://",
                    str(env["DATABASE_USER"]),
                    ":",
                    str(env["DATABASE_PASSWORD"]),
                    "@",
                    str(env["DATABASE_HOST"]),
                    ":",
                    str(env["DATABASE_PORT"]),
                    "/",
                    str(env["DATABASE_SCHEMA"]),
                ]
            )

        REDIS_HOST = env["REDIS_HOST"]
        REDIS_PORT = env["REDIS_PORT"]
        REDIS_DB = int(env["REDIS_DB"])
        REDIS_PASSWORD = env["REDIS_PASSWORD"]

        WEBHOOK_SECRET = env["WEBHOOK_SECRET"]

        CELERY: Dict[str, str | bool] = {
            "broker_url": f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/6",
            "result_backend": f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/7",
            "task_ignore_result": True,
            "broker_connection_retry_on_startup": True,
            "timezone": "America/Sao_Paulo",
        }

    except Exception as e:
        raise e
