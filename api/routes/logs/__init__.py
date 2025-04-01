"""Module for the logs routes."""

from importlib import import_module
from pathlib import Path

from quart import Blueprint

path_template = str(Path(__file__).parent.resolve().joinpath("templates"))
logsbot = Blueprint("logsbot", __name__, template_folder=path_template)


def imports() -> None:
    """Import the routes for the logs module."""
    import_module(".route", __package__)
    import_module(".logbot", __package__)


imports()
