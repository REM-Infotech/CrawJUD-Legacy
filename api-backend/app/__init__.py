"""Api CrawJUD."""

from pathlib import Path

from dotenv import load_dotenv
from dynaconf import FlaskDynaconf
from flask import Flask
from passlib.context import CryptContext

from app._types import MyAny as MyAny
from app.config import settings

app = Flask(__name__)

load_dotenv()

path_passlib_config = str(Path.cwd().joinpath("passlib.conf"))
crypt_context = CryptContext.from_path(path_passlib_config)


def create_app() -> Flask:
    """Create Flask application.

    Args:
        config_name (ConfigNames): Configuration name.

    Returns:
        Flask: Flask application.

    """
    global app, io

    with app.app_context():
        FlaskDynaconf(
            app,
            instance_relative_config=True,
            extensions_list="EXTENSIONS",  # pyright: ignore[reportArgumentType]
            dynaconf_instance=settings,
        )

    return app
