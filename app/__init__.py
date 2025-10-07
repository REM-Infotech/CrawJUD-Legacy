"""Api CrawJUD."""

from dynaconf import FlaskDynaconf
from flask import Flask

from app._types import ConfigNames

app = Flask(__name__)


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
        extensions_list="EXTENSIONS",  # pyright: ignore[reportArgumentType]
        settings_files=["settings.yaml"],
        load_dotenv=True,
        environments=True,
    )

    with app.app_context():
        app.config.load_extensions()  # pyright: ignore[reportAttributeAccessIssue]

    return app
