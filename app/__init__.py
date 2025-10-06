import os
from typing import Iterable
from wsgiref.types import StartResponse, WSGIEnvironment

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from app.config.extensions import start_extensions

db = SQLAlchemy


def create_app(config_name=None) -> Flask:
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development").capitalize() + "Config"

    app = Flask(__name__)

    from app import conf

    config_class = getattr(conf, config_name, conf.DevelopmentConfig)
    app.config.from_object(config_class)

    # Importa e registra blueprints de rotas
    from app.routes import register_routes

    start_extensions(app)
    app = register_routes(app)

    def response(
        environ: WSGIEnvironment,
        start_response: StartResponse,
    ) -> Iterable[bytes]:
        start_response("404 OK", [("Content-Type", "text/plain")])
        return iter([b"Not Found"])

    # Remove the default route mapping, so only "/api/v1" is served
    app.wsgi_app = DispatcherMiddleware(
        # Return a 404 for anything outside "/api/v1"
        response,
        {"/api/v1": app},
    )
    return app
