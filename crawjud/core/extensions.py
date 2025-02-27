"""Application extensions module."""

from os import getenv

from quart import Quart
from redis import Redis
from socketio import AsyncRedisManager, AsyncServer

from crawjud.core import db, login_manager, mail


async def init_extensions(app: Quart) -> AsyncServer:
    """Initialize and configure the application extensions."""
    from crawjud._utils import check_allowed_origin

    from .database import database_start
    from .security import security_config

    host_redis = getenv("REDIS_HOST")
    pass_redis = getenv("REDIS_PASSWORD")
    port_redis = getenv("REDIS_PORT")
    database_redis = getenv("REDIS_DB_LOGS")
    database_redis_io = getenv("REDIS_DB_IO")
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    redis_manager = AsyncRedisManager(url=f"redis://:{pass_redis}@{host_redis}:{port_redis}/{database_redis_io}")
    io = AsyncServer(
        async_mode="asgi",
        cors_allowed_origins=check_allowed_origin,
        client_manager=redis_manager,
        ping_interval=25,
        ping_timeout=10,
    )
    await database_start(app)
    await security_config(app)

    app.extensions["redis"] = Redis(host=host_redis, port=port_redis, password=pass_redis, db=database_redis)
    app.extensions["socketio"] = io

    return io
