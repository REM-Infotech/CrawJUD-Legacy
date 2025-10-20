"""Api CrawJUD."""

from pathlib import Path

from __types import MyAny as MyAny
from dotenv import load_dotenv
from dynaconf import Dynaconf, FlaskDynaconf
from flask import Flask
from passlib.context import CryptContext

app = Flask(__name__)
load_dotenv(Path.cwd().parent)

path_passlib_config = str(Path.cwd().joinpath("passlib.conf"))
crypt_context = CryptContext.from_path(path_passlib_config)


def create_app() -> Flask:
    """Create Flask application.

    Returns:
        Flask: Flask application.

    """
    settings = Dynaconf(
        lowercase_read=False,
        root_path=str(Path.cwd().parent.joinpath("config").resolve()),
        envvar_prefix="CRAWJUD",
        settings_files=["settings.yaml"],
        environments=True,
        load_dotenv=True,
        commentjson_enabled=True,
        merge_enabled=True,
        dotenv_override=True,
        env="celery",
    )

    FlaskDynaconf(
        app=app,
        instance_relative_config=True,
        extensions_list="EXTENSIONS",  # pyright: ignore[reportArgumentType]
        dynaconf_instance=settings,
    )
    return app
