"""Module for logs routes."""

from importlib import import_module
from pathlib import Path

from quart import Blueprint

path_template = Path(__file__).parent.resolve().joinpath("templates")
logsbot = Blueprint("logsbot", __name__, template_folder=path_template)


def import_routes() -> None:
    """Import all routes in the logs module."""
    import_module(".websocket", package=__package__)
    import_module(".execution", package=__package__)


import_routes()
