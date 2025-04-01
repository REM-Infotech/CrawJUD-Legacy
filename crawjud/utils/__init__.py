"""Miscellaneous utilities and helpers for the CrawJUD-Bots application."""

import secrets
import subprocess

from dotenv_vault import load_dotenv

from .check_cors import check_allowed_origin
from .gcs_mgmt import get_file
from .gen_seed import worker_name_generator
from .get_location import GeoLoc
from .make_celery import make_celery
from .scheduler import DatabaseScheduler
from .status import (
    TaskExec,
    enviar_arquivo_para_gcs,
    format_message_log,
    load_cache,
    makezip,
)


def gerar_cor_base() -> tuple[int, int, int]:
    r = secrets.randbelow(256)
    g = secrets.randbelow(256)
    b = secrets.randbelow(256)
    return r, g, b


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def escurecer_cor(r: int, g: int, b: int, fator: int = 0.85) -> tuple[int, int, int]:
    return int(r * fator), int(g * fator), int(b * fator)


def get_hostname() -> str:
    """Get the hostname of the current machine."""
    return subprocess.run(
        [
            "powershell",
            "hostname",
        ],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()


signed_url_lifetime = 300
__all__ = [
    get_hostname,
    worker_name_generator,
    DatabaseScheduler,
    GeoLoc,
    check_allowed_origin,
    make_celery,
    makezip,
    enviar_arquivo_para_gcs,
    get_file,
    load_cache,
    format_message_log,
    TaskExec,
]

load_dotenv()
