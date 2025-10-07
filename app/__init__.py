"""Api CrawJUD."""

from dotenv import load_dotenv
from dynaconf import FlaskDynaconf
from flask import Flask

from app._types import ConfigNames
from app.config import settings

app = Flask(__name__)

load_dotenv()


def create_app(config_name: ConfigNames = "DevelopmentConfig") -> Flask:
    """Create Flask application.

    Args:
        config_name (ConfigNames): Configuration name.

    Returns:
        Flask: Flask application.

    """
    global app

    FlaskDynaconf(
        app,
        instance_relative_config=True,
        extensions_list="EXTENSIONS",  # pyright: ignore[reportArgumentType]
        dynaconf_instance=settings,
    )

    with app.app_context():
        app.config.load_extensions()  # pyright: ignore[reportAttributeAccessIssue]

    return app
