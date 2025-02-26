"""Configuration loader module for the application.

This module provides functionality to load configuration settings
into a Quart application instance from various sources.
"""

import os
from pathlib import Path

from celery.app.base import Celery
from quart import Quart
from socketio import ASGIApp

objects_config = {
    "development": "crawjud.app.config.DevelopmentConfig",
    "production": "crawjud.app.config.ProductionConfig",
    "testing": "crawjud.app.config.TestingConfig",
}


async def app_configurator(app: Quart) -> tuple[Quart, ASGIApp, Celery]:
    """Load configuration settings into the Quart application.

    Args:
        app: The Quart application instance to configure

    Returns:
        None

    """
    env_ambient = os.getenv("AMBIENT_CONFIG")
    ambient = objects_config[env_ambient]
    app.config.from_object(ambient)

    async with app.app_context():
        from crawjud.utils import make_celery

        from .extensions import init_extensions
        from .routing import register_routes

        celery = await make_celery(app)
        celery.set_default()
        app.extensions["celery"] = celery

        celery.autodiscover_tasks(["bot", "utils"])

        io = await init_extensions(app)

        folder_logs = Path(__file__).cwd().joinpath("logs").resolve()
        folder_logs.mkdir(exist_ok=True)

        logfile = folder_logs.joinpath("%s.log" % os.getenv("APPLICATION_APP", "asgi"))
        logfile.touch(exist_ok=True)

        await register_routes(app)

    return app, ASGIApp(io, app), celery
