"""Objeto das configurações do app."""

from pathlib import Path

from dynaconf import Dynaconf

setting_file = str(Path.cwd().joinpath("config", "settings.yaml"))
settings = Dynaconf(
    lowercase_read=False,
    envvar_prefix="CRAWJUD",
    settings_files=[setting_file],
    environments=True,
    load_dotenv=True,
    commentjson_enabled=True,
    merge_enabled=True,
    dotenv_override=True,
    env="celery",
)
