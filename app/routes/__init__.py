import eventlet

eventlet.monkey_patch(socket=True)

from importlib import import_module

from dotenv import dotenv_values
from flask import Flask, Response, make_response, redirect
from werkzeug.exceptions import HTTPException


def register_routes(app: Flask) -> None:

    import_module("app.routes.logs", package=__package__)
    from ..routes.bot import bot
    from ..routes.webhook import wh

    app.register_blueprint(wh)
    app.register_blueprint(bot)

    @app.errorhandler(HTTPException)
    def handle_http_exception(error) -> Response:

        url = dotenv_values().get("url_web")
        return make_response(redirect(url))
