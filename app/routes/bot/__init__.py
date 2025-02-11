"""Bot blueprint module."""

from importlib import import_module
from pathlib import Path

from quart import Blueprint

path_template = str(Path(__file__).parent.resolve().joinpath("templates"))
bot = Blueprint("bot", __name__, template_folder=path_template)


def import_modules() -> None:
    """Import modules for the bot package."""
    import_module(".route", package=__package__)
    import_module(".task_exec", package=__package__)


import_modules()
