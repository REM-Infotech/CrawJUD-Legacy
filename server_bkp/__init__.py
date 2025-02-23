"""Module for manage application with System Status and System Information."""

from importlib import import_module
from os import getenv
from pathlib import Path

import quart_flask_patch  # noqa: F401
from flask_sqlalchemy import SQLAlchemy
from quart import Quart
from socketio import ASGIApp, AsyncServer

instance_dir = Path(__file__).parent.resolve().joinpath("instance")
template_dir = Path(__file__).parent.resolve().joinpath("templates")
static_dir = Path(__file__).parent.resolve().joinpath("static")


app = Quart(
    __name__,
    template_folder=str(template_dir),
    static_folder=str(static_dir),
    instance_path=str(instance_dir),
)
db = SQLAlchemy()
io = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_interval=25,
    ping_timeout=10,
)


objects_config = {
    "development": "server.config.DevelopmentConfig",
    "production": "server.config.ProductionConfig",
    "testing": "server.config.TestingConfig",
}


async def create_app() -> Quart:
    """Create and configure the Quart application."""
    from server.routes import register_blueprint

    import_module("server.logs", __package__)
    await register_blueprint()
    env_ambient = getenv("AMBIENT_CONFIG")
    ambient = objects_config[env_ambient]
    app.config.from_object(ambient)
    db.init_app(app)

    return ASGIApp(io, app)
