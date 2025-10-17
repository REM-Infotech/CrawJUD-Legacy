"""Api CrawJUD."""

from pathlib import Path

from dotenv import load_dotenv
from dynaconf import Dynaconf, FlaskDynaconf
from flask import Flask
from passlib.context import CryptContext
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from app._types import MyAny as MyAny

app = Flask(__name__)
root_app = Flask("root_app")
bots_app = Flask("bots_app")
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

    config = FlaskDynaconf(
        instance_relative_config=True,
        extensions_list="EXTENSIONS",  # pyright: ignore[reportArgumentType]
        dynaconf_instance=settings,
    )
    config.init_app(app)
    config.init_app(root_app)
    config.init_app(bots_app)

    app.wsgi_app = DispatcherMiddleware(
        app.wsgi_app,
        {"/api/v1": root_app.wsgi_app, "/api/v1/bots": bots_app.wsgi_app},
    )

    return app
