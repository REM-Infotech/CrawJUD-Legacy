"""CrawJUD - Sistema de Automação Jurídica."""

import importlib
from pathlib import Path

from celery import Celery
from dynaconf import Dynaconf

import _hook as _

setting_file = str(Path.cwd().joinpath("config", "settings.yaml"))
settings = Dynaconf(
    lowercase_read=False,
    root_path=setting_file,
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

    Returns:
        Celery: Configured Celery instance.

    """
    app = Celery(__name__)
    dict_config = {k.lower(): v for k, v in list(settings.as_dict().items())}
    app.config_from_object(dict_config)
    importlib.import_module("tasks", __package__)

    return app


app = make_celery()
