from flask import Flask

from app import conf
from app._types import ConfigNames
from app.config.extensions import start_extensions

app = Flask(__name__)


def create_app(config_name: ConfigNames = "DevelopmentConfig") -> Flask:
    from app.routes import register_routes

    global app
    config_class = getattr(conf, config_name, conf.DevelopmentConfig)
    app.config.from_object(config_class)

    start_extensions(app)
    return register_routes(app)
