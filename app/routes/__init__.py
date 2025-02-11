"""Route registration and error handling for the CrawJUD-Bots application."""

from importlib import import_module
from os import environ

from dotenv_vault import load_dotenv
from quart import Quart, Response, make_response, redirect
from werkzeug.exceptions import HTTPException

load_dotenv()


async def register_routes(app: Quart) -> None:
    """Register blueprints and error handlers with the Quart application.

    Args:
        app (Quart): The Quart application instance.

    """
    async with app.app_context():
        import_module(".logs", package=__package__)

    from app.routes.bot import bot
    from app.routes.webhook import wh

    app.register_blueprint(wh)
    app.register_blueprint(bot)

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException) -> Response:
        url = environ.get("URL_WEB")
        return make_response(redirect(url))
