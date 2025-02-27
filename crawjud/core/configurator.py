"""Configuration loader module for the application.

This module provides functionality to load configuration settings
into a Quart application instance from various sources.
"""

import logging
import os
import subprocess
from pathlib import Path

from celery.app.base import Celery
from quart import Quart
from socketio import ASGIApp
from uvicorn import Config, Server

from crawjud.logs import log_cfg

objects_config = {
    "development": "crawjud.config.DevelopmentConfig",
    "production": "crawjud.config.ProductionConfig",
    "testing": "crawjud.config.TestingConfig",
}


def get_hostname() -> str:
    """Get the hostname of the current machine."""
    return subprocess.run(
        [
            "powershell",
            "hostname",
        ],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()


async def app_configurator(app: Quart) -> tuple[Quart, Server, ASGIApp, Celery]:
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

        celery = None
        celery = await make_celery(app)
        celery.set_default()
        app.extensions["celery"] = celery

        celery.autodiscover_tasks(["crawjud.bot", "crawjud.utils"])

        io = await init_extensions(app)

        folder_logs = Path(__file__).cwd().joinpath("logs").resolve()
        folder_logs.mkdir(exist_ok=True)

        logfile = folder_logs.joinpath("%s.log" % os.getenv("APPLICATION_APP", "asgi"))
        logfile.touch(exist_ok=True)

        await register_routes(app)

        cfg, _ = log_cfg()
        port = os.getenv("SERVER_PORT", 5000)
        hostname = os.getenv(
            "SERVER_HOSTNAME",
            get_hostname(),
        )

        log_level = logging.INFO
        if os.getenv("DEBUG", "False").lower() == "true":
            log_level = logging.DEBUG

        asgi = ASGIApp(io, app)
        cfg = Config(
            asgi,
            host=hostname,
            port=port,
            log_config=cfg,
            log_level=log_level,
        )
        srv = Server(cfg)

    return app, srv, asgi, celery
