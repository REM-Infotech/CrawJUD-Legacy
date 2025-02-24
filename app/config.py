"""Configuration module for CrawJUD-Bots application."""

from __future__ import annotations

import logging
import secrets
from datetime import timedelta
from os import environ
from pathlib import Path

from dotenv_vault import load_dotenv

load_dotenv()


class Config:
    """Base configuration class."""

    LOG_LEVEL = logging.INFO
    DEBUG: type[bool] = False
    TESTING: type[bool] = False
    SECRET_KEY: type[str] = secrets.token_hex()
    TEMPLATES_AUTO_RELOAD: type[bool] = False

    # FLASK-MAIL CONFIG
    MAIL_SERVER: type[str] = ""
    MAIL_PORT: type[int] = 587
    MAIL_USE_TLS: type[bool] = False
    MAIL_USE_SSL: type[bool] = False
    MAIL_USERNAME: type[str] = ""
    MAIL_PASSWORD: type[str] = ""
    MAIL_DEFAULT_SENDER: type[str] = ""

    # SQLALCHEMY CONFIG
    SQLALCHEMY_POOL_SIZE: type[int] = 30  # Número de conexões na pool

    # Número de conexões extras além da pool_size
    SQLALCHEMY_MAX_OVERFLOW: type[int] = 10

    # Tempo de espera para obter uma conexão
    SQLALCHEMY_POOL_TIMEOUT: type[int] = 30

    # Tempo (em segundos) para reciclar as conexões ociosas
    SQLALCHEMY_POOL_RECYCLE: type[int] = 1800

    # Verificar a saúde da conexão antes de usá-la
    SQLALCHEMY_POOL_PRE_PING: type[bool] = True

    SQLALCHEMY_BINDS: dict[str, str] = {"cachelogs": "sqlite:///cachelogs.db"}
    SQLALCHEMY_DATABASE_URI: type[str] = "sqlite:///local.db"
    SQLALCHEMY_ENGINE_OPTIONS: dict[str, str | bool] = {"pool_pre_ping": True}
    SQLALCHEMY_TRACK_MODIFICATIONS: type[bool] = False

    # FLASK CONFIG
    PREFERRED_URL_SCHEME: type[str] = "https"
    SESSION_COOKIE_HTTPONLY: type[bool] = False
    SESSION_COOKIE_SECURE: type[bool] = True
    PERMANENT_SESSION_LIFETIME: type[int] = timedelta(days=31).max.seconds

    TEMP_PATH: Path = Path(__file__).cwd().joinpath("bot/temp").resolve()
    ARCHIVES: Path = Path(__file__).cwd().joinpath("bot/Archives").resolve()
    TEMP_PATH.mkdir(exist_ok=True)
    ARCHIVES.mkdir(exist_ok=True)

    WEBHOOK_SECRET: type[str] = ""

    REDIS_HOST: type[str] = ""
    REDIS_PORT: type[int] = 6379
    REDIS_DB: type[str] = ""
    REDIS_PASSWORD: type[str] = ""

    BROKER_DATABASE: type[int] = 1
    RESULT_BACKEND_DATABASE: type[int] = 2

    ARCHIVES_PATH = str(Path(__file__).cwd().joinpath("Archives"))
    resolved_archives = Path(ARCHIVES_PATH).resolve()

    PDF_PATH = str(resolved_archives.joinpath("PDF"))
    DOCS_PATH = str(resolved_archives.joinpath("Docs"))
    TEMP_DIR = str(resolved_archives.joinpath("Temp"))
    IMAGE_TEMP_DIR = str(resolved_archives.joinpath(TEMP_DIR, "IMG"))
    CSV_TEMP_DIR = str(resolved_archives.joinpath(TEMP_DIR, "csv"))
    PDF_TEMP_DIR = str(resolved_archives.joinpath(TEMP_DIR, "pdf"))
    SRC_IMG_PATH = str(Path(__file__).cwd().resolve().joinpath("web", "src", "assets", "img"))

    Path(ARCHIVES_PATH).rmdir(exist_ok=True)
    Path(ARCHIVES_PATH).mkdir(exist_ok=True)

    for paths in [
        DOCS_PATH,
        TEMP_DIR,
        IMAGE_TEMP_DIR,
        CSV_TEMP_DIR,
        PDF_TEMP_DIR,
    ]:
        Path(paths).mkdir(exist_ok=True, parents=True)

    CSP: dict[str, str | list[str] | list[list[str]]] = {
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
    """Configuration settings for production environment."""

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
        ],
    )

    REDIS_HOST = env["REDIS_HOST"]
    REDIS_PORT = env["REDIS_PORT"]
    REDIS_DB = int(env["REDIS_DB_LOGS"])
    REDIS_PASSWORD = env["REDIS_PASSWORD"]
    REDIS_URL = env["REDIS_URL"]

    BROKER_DATABASE = int(env["BROKER_DATABASE"])
    RESULT_BACKEND_DATABASE = int(env["RESULT_BACKEND_DATABASE"])
    WEBHOOK_SECRET = env["WEBHOOK_SECRET"]

    CELERY: dict[str, str | bool] = {
        "broker_url": f"{REDIS_URL}/{BROKER_DATABASE}",
        "result_backend": f"{REDIS_URL}/{RESULT_BACKEND_DATABASE}",
        "task_ignore_result": True,
        "broker_connection_retry_on_startup": True,
        "timezone": "America/Sao_Paulo",
        "task_create_missing_queues": True,
    }


class DevelopmentConfig(Config):
    """Configuration settings for development environment."""

    env = environ
    LOG_LEVEL = logging.DEBUG
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
            ],
        )

    REDIS_HOST = env["REDIS_HOST"]
    REDIS_PORT = env["REDIS_PORT"]
    REDIS_DB = int(env["REDIS_DB_LOGS"])
    REDIS_PASSWORD = env["REDIS_PASSWORD"]
    REDIS_URL = env["REDIS_URL"]

    BROKER_DATABASE = int(env["BROKER_DATABASE"])
    RESULT_BACKEND_DATABASE = int(env["RESULT_BACKEND_DATABASE"])
    WEBHOOK_SECRET = env["WEBHOOK_SECRET"]

    CELERY: dict[str, str | bool] = {
        "broker_url": f"{REDIS_URL}/{BROKER_DATABASE}",
        "result_backend": f"{REDIS_URL}/{RESULT_BACKEND_DATABASE}",
        "task_ignore_result": True,
        "broker_connection_retry_on_startup": True,
        "timezone": "America/Manaus",
        "task_create_missing_queues": True,
    }


class TestingConfig(Config):
    """Configuration settings for testing environment."""

    TESTTING = True
    env = environ
    LOG_LEVEL = logging.DEBUG
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
            ],
        )

    REDIS_HOST = env["REDIS_HOST"]
    REDIS_PORT = env["REDIS_PORT"]
    REDIS_DB = int(env["REDIS_DB_LOGS"])
    REDIS_PASSWORD = env["REDIS_PASSWORD"]
    REDIS_URL = env["REDIS_URL"]

    BROKER_DATABASE = int(env["BROKER_DATABASE"])
    RESULT_BACKEND_DATABASE = int(env["RESULT_BACKEND_DATABASE"])
    WEBHOOK_SECRET = env["WEBHOOK_SECRET"]

    CELERY: dict[str, str | bool] = {
        "broker_url": f"{REDIS_URL}/{BROKER_DATABASE}",
        "result_backend": f"{REDIS_URL}/{RESULT_BACKEND_DATABASE}",
        "task_ignore_result": True,
        "broker_connection_retry_on_startup": True,
        "timezone": "America/Sao_Paulo",
        "task_create_missing_queues": True,
    }
