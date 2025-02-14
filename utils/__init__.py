"""Miscellaneous utilities and helpers for the CrawJUD-Bots application."""

from dotenv_vault import load_dotenv

from .bots_logs import (
    asyncinit_log,
    init_log,
)
from .check_cors import check_allowed_origin
from .gcs_mgmt import get_file
from .get_location import GeoLoc
from .git_py import _release_tag, check_latest, checkout_release, update_servers, version_file
from .make_celery import make_celery
from .mod_mgmt import reload_module
from .scheduler import DatabaseScheduler
from .status import (
    FormatMessage,
    email_start,
    email_stop,
    enviar_arquivo_para_gcs,
    load_cache,
    makezip,
)

signed_url_lifetime = 300
__all__ = [
    DatabaseScheduler,
    _release_tag,
    check_latest,
    checkout_release,
    update_servers,
    GeoLoc,
    check_allowed_origin,
    make_celery,
    init_log,
    asyncinit_log,
    version_file,
    makezip,
    email_start,
    email_stop,
    enviar_arquivo_para_gcs,
    get_file,
    load_cache,
    FormatMessage,
    reload_module,
]

load_dotenv()
