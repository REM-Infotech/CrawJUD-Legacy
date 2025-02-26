"""Miscellaneous utilities and helpers for the CrawJUD-Bots application."""

from dotenv_vault import load_dotenv

from ..check_cors import check_allowed_origin
from ..gcs_mgmt import get_file
from ..gen_seed import worker_name_generator
from ..get_location import GeoLoc
from ..git_py import _release_tag, check_latest, checkout_release, update_servers, version_file
from ..make_celery import make_celery
from ..mod_mgmt import reload_module
from ..scheduler import DatabaseScheduler
from ..status import (
    TaskExec,
    enviar_arquivo_para_gcs,
    format_message_log,
    load_cache,
    makezip,
)

signed_url_lifetime = 300
__all__ = [
    worker_name_generator,
    DatabaseScheduler,
    _release_tag,
    check_latest,
    checkout_release,
    update_servers,
    GeoLoc,
    check_allowed_origin,
    make_celery,
    version_file,
    makezip,
    enviar_arquivo_para_gcs,
    get_file,
    load_cache,
    format_message_log,
    reload_module,
    TaskExec,
]

load_dotenv()
