"""Configuração do app usando Dynaconf."""

from pathlib import Path

from dynaconf import Dynaconf

settings = Dynaconf(
    lowercase_read=False,
    root_path=str(Path(__file__).parent.resolve()),
    envvar_prefix="CRAWJUD",
    settings_files=["settings.yaml"],
    environments=True,
    load_dotenv=True,
    commentjson_enabled=True,
    merge_enabled=True,
    dotenv_override=True,
    env="CELERY",
)
