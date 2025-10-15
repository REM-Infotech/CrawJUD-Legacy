"""Configuração do app usando Dynaconf."""

import os
from pathlib import Path

from dynaconf import Dynaconf

settings = Dynaconf(
    root_path=str(Path(__file__).parent.resolve()),
    envvar_prefix="CRAWJUD",
    settings_files=["settings.yaml"],
    environments=True,
    load_dotenv=True,
    commentjson_enabled=True,
    merge_enabled=True,
    dotenv_override=True,
    env=os.environ.get("CRAWJUD_ENV", "default").lower(),
)
