"""CrawJUD - Sistema de Automação Jurídica."""

import importlib
from pathlib import Path

import resources._hook as _
from celery import Celery
from dynaconf import Dynaconf

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
    env="CELERY",
    default_env="api",
)


__all__ = ["_"]


def make_celery() -> Celery:
    """Create and configure a Celery instance with Quart application context.

    Args:
        app (Quart): The Quart application instance.

    Returns:
        Celery: Configured Celery instance.

    """
    app = Celery(__name__)
    dict_config = {k.lower(): v for k, v in list(settings.as_dict().items())}
    app.config_from_object(dict_config)
    importlib.import_module("tasks", __package__)

    return app


app = make_celery()
