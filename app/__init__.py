import os
from typing import Iterable, cast
from wsgiref.types import StartResponse, WSGIEnvironment

from flask import Flask

from app import conf
from app._types import ConfigNames
from app.config.extensions import start_extensions

app = Flask(__name__)


def response(
    environ: WSGIEnvironment,
    start_response: StartResponse,
) -> Iterable[bytes]:
    start_response("404 OK", [("Content-Type", "text/plain")])
    return iter([b"Not Found"])


def create_app(config_name: ConfigNames | None = None) -> Flask:
    from app.routes import register_routes

    global app
    if config_name is None:
        config_name = cast(
            ConfigNames,
            os.environ.get("FLASK_ENV", "development").capitalize() + "Config",
        )

    config_class = getattr(conf, config_name, conf.DevelopmentConfig)
    app.config.from_object(config_class)

    # Importa e registra blueprints de rotas

    start_extensions(app)
    return register_routes(app)
