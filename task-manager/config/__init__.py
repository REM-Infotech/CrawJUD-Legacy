"""Configurações celery."""

from pathlib import Path

from dynaconf import Dynaconf

setting_file = str(Path(__file__).parent.joinpath("settings.yaml"))
config = Dynaconf(
    lowercase_read=False,
    root_path=setting_file,
    envvar_prefix="CRAWJUD",
    settings_files=[setting_file],
    environments=True,
    load_dotenv=True,
    commentjson_enabled=True,
    merge_enabled=True,
    dotenv_override=True,
    default_env="api",
)
