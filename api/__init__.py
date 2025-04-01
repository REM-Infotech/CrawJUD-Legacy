"""Quart application package."""

import re
from datetime import timedelta
from importlib import import_module
from os import getenv
from pathlib import Path

import aiofiles
import quart_flask_patch  # noqa: F401
from celery import Celery
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from hypercorn.middleware.proxy_fix import ProxyFixMiddleware as ProxyHeadersMiddleware
from quart import Quart
from quart_cors import cors
from quart_jwt_extended import JWTManager
from redis import Redis
from socketio import ASGIApp, AsyncRedisManager, AsyncServer

app = Quart(__name__)
mail = Mail()
jwt = JWTManager()
db = SQLAlchemy()
tlsm = Talisman()


async def create_celery_app() -> Celery:
    """Load configuration settings into the Quart application.

    Args:
        app: The Quart application instance to configure

    Returns:
        Celery: The Celery application instance

    """
    from crawjud.utils import make_celery

    async with app.app_context():
        celery = None
        celery = await make_celery(app)
        celery.set_default()
        app.extensions["celery"] = celery
        celery.autodiscover_tasks(["crawjud.bot", "crawjud.utils"])

    return celery


async def security_config(app: Quart) -> None:
    """Configure the application security settings."""
    # # Configure the Content Security Policy (CSP) for the application.
    tlsm.init_app(
        app,
        content_security_policy=app.config["CSP"],
        session_cookie_http_only=True,
        session_cookie_samesite="Lax",
        strict_transport_security=True,
        strict_transport_security_max_age=timedelta(days=31).max.seconds,
        x_content_type_options=True,
    )


async def database_start(app: Quart) -> None:
    """Initialize and configure the application database.

    This function performs the following tasks:
    1. Checks if the current server exists in the database
    2. Creates a new server entry if it doesn't exist
    3. Initializes all database tables

    Args:
        app (Quart): The Quart application instance

    Returns:
        None

    Note:
        This function requires the following environment variables:
        - NAMESERVER: The name of the server
        - HOSTNAME: The address of the server

    """
    from api.models import init_database

    if not Path("is_init.txt").exists():
        async with aiofiles.open("is_init.txt", "w") as f:
            await f.write(f"{await init_database(app, db)}")

    from api.models import Users

    if not db.engine.dialect.has_table(db.engine.connect(), Users.__tablename__):
        async with aiofiles.open("is_init.txt", "w") as f:
            await f.write(f"{await init_database(app, db)}")


async def register_routes(app: Quart) -> None:
    """Register application's blueprints and error handlers with the Quart instance.

    This function manages the application's routing configuration by:
    1. Dynamically importing required route modules
    2. Registering blueprints for bot and webhook endpoints
    3. Setting up application-wide error handlers

    Args:
        app (Quart): The Quart application instance to configure

    Returns:
        None

    Note:
        Currently registers 'bot' and 'webhook' blueprints, and imports
        logs routes automatically.

    """
    async with app.app_context():
        # Dynamically import additional route modules as needed.
        import_module("api.routes.logs", package=__package__)
        import_module("api.routes", package=__package__)

    from api.routes.auth import auth
    from api.routes.bot import bot
    from api.routes.config import admin
    from api.routes.credentials import cred
    from api.routes.dashboard import dash
    from api.routes.execution import exe
    from api.routes.logs import logsbot

    listBlueprints = [bot, auth, logsbot, exe, dash, cred, admin]  # noqa: N806

    for bp in listBlueprints:
        app.register_blueprint(bp)


async def init_extensions(app: Quart) -> AsyncServer:
    """Initialize and configure the application extensions."""
    from crawjud.utils import check_allowed_origin

    host_redis = getenv("REDIS_HOST")
    pass_redis = getenv("REDIS_PASSWORD")
    port_redis = getenv("REDIS_PORT")
    database_redis = getenv("REDIS_DB_LOGS")
    database_redis_io = getenv("REDIS_DB_IO")
    mail.init_app(app)
    db.init_app(app)
    # login_manager.init_app(app)
    jwt.init_app(app)
    redis_manager = AsyncRedisManager(url=f"redis://:{pass_redis}@{host_redis}:{port_redis}/{database_redis_io}")
    io = AsyncServer(
        async_mode="asgi",
        cors_allowed_origins=check_allowed_origin,
        client_manager=redis_manager,
        ping_interval=25,
        ping_timeout=10,
        namespaces=["/bot", "/logs"],
    )

    async with app.app_context():
        await database_start(app)
        await security_config(app)
        await create_celery_app()

    app.extensions["redis"] = Redis(host=host_redis, port=port_redis, password=pass_redis, db=database_redis)
    app.extensions["socketio"] = io

    return io


async def create_app(confg: object) -> ASGIApp:
    """Create and configure the Quart application instance."""
    app.config.from_object(confg)

    async with app.app_context():
        io = await init_extensions(app)
        await register_routes(app)

    allowed_origins = [
        "https://crawjud.reminfotech.net.br",
        re.compile(r"http://127\.0\.0\.1:\d*"),
        re.compile(r"http://\d*\.\d*\.\d*:\d*"),
        re.compile(r"http://localhost:\d*"),
        re.compile(r"https://.*\.reminfotech\.net\.br"),
        re.compile(r"https://.*\.nicholas\.dev\.br"),
        re.compile(r"https://.*\.robotz\.dev"),
        re.compile(r"https://.*\.rhsolutions\.info"),
        re.compile(r"https://.*\.rhsolut\.com\.br"),
    ]
    app.asgi_app = ProxyHeadersMiddleware(app.asgi_app)
    return ASGIApp(
        io,
        cors(
            app,
            allow_origin=allowed_origins,
            allow_credentials=True,
            allow_methods=["POST", "OPTIONS", "GET"],
            allow_headers=["Content-Type", "Authorization", "x-csrf-token", "X-CSRF-TOKEN"],
        ),
    )
