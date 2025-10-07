from flask import Flask

from app import conf
from app._types import ConfigNames
from app.config.extensions import start_extensions

app = Flask(__name__)


def create_app(config_name: ConfigNames = "DevelopmentConfig") -> Flask:
    global app
    config_class = getattr(conf, config_name, conf.DevelopmentConfig)
    app.config.from_object(config_class)

    start_extensions(app)

    with app.app_context():
        from app.routes import register_routes

        return register_routes(app)
