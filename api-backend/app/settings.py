"""Objeto das configurações do app."""

from dynaconf import Dynaconf

settings = Dynaconf(
    lowercase_read=False,
    envvar_prefix="CRAWJUD",
    settings_files=["settings.yaml"],
    environments=True,
    load_dotenv=True,
    commentjson_enabled=True,
    merge_enabled=True,
    dotenv_override=True,
    env="celery",
)
