"""Route registration module for the CrawJUD-Bots application.

This module is responsible for dynamically importing route modules, registering blueprints,
and setting up global error handlers for the Quart application.
"""

from importlib import import_module
from os import environ

from dotenv_vault import load_dotenv
from quart import Quart, Response, make_response, redirect
from werkzeug.exceptions import HTTPException

load_dotenv()


async def register_routes(app: Quart) -> None:
    """Register application's blueprints and error handlers with the Quart instance.

    This function imports route modules, registers the defined blueprints,
    and sets up a single error handler for HTTP exceptions.

    Args:
        app (Quart): The Quart application instance.

    Returns:
        None

    """
    async with app.app_context():
        # Dynamically import additional route modules as needed.
        import_module(".logs", package=__package__)

    from app.routes.bot import bot
    from app.routes.webhook import wh

    # Register the blueprints for bot and webhook endpoints.
    app.register_blueprint(wh)
    app.register_blueprint(bot)

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException) -> Response:  # pragma: no cover
        # Redirect to a specified URL in case of HTTP exceptions.
        url = environ.get("URL_WEB")
        return make_response(redirect(url))
