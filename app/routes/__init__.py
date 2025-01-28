from importlib import import_module

from os import environ
from dotenv_vault import load_dotenv
from flask import Flask, Response, make_response, redirect
from werkzeug.exceptions import HTTPException


load_dotenv()


def register_routes(app: Flask) -> None:

    import_module(".logs", package=__package__)
    from ..routes.bot import bot
    from ..routes.webhook import wh

    app.register_blueprint(wh)
    app.register_blueprint(bot)

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException) -> Response:

        url = environ.get("url_web")
        return make_response(redirect(url))
