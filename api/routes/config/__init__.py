"""Config blueprint for admin routes."""

from importlib import import_module
from os import path
from pathlib import Path

from quart import Blueprint

path_template = path.join(Path(__file__).parent.resolve(), "templates")
admin = Blueprint("admin", __name__, template_folder=path_template)


def import_routes() -> None:
    """Import routes."""
    import_module(".users", __package__)


import_routes()
