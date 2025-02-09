"""Blueprint for managing bot operations such as launching, stopping, and scheduling."""

from importlib import import_module
from pathlib import Path

from quart import Blueprint

path_template = Path(__file__).parent.resolve().joinpath("templates")
bot = Blueprint("bot", __name__, template_folder=path_template)


if bot is not None:

    def import_routes() -> None:
        """Import the bot operation routes."""
        import_module(".front", package=__package__)
        import_module(".back", package=__package__)

    import_routes()
