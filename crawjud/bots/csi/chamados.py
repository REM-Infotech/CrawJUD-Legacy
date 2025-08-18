# noqa: D100
from __future__ import annotations

import secrets  # noqa: F401
import traceback  # noqa: F401
from contextlib import suppress  # noqa: F401
from threading import Thread  # noqa: F401
from time import sleep  # noqa: F401
from typing import TYPE_CHECKING, ClassVar  # noqa: F401

from dotenv import load_dotenv
from httpx import Client  # noqa: F401
from tqdm import tqdm  # noqa: F401

from crawjud.bots.controllers.csi import CsiBot
from crawjud.bots.controllers.pje import PjeBot  # noqa: F401
from crawjud.common.exceptions.bot import ExecutionError  # noqa: F401
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task, wrap_cls
from crawjud.utils.formatadores import formata_tempo  # noqa: F401

if TYPE_CHECKING:
    from concurrent.futures import Future  # noqa: F401
    from datetime import datetime  # noqa: F401

    from crawjud.interfaces.types import BotData  # noqa: F401
    from crawjud.interfaces.types.pje import DictResults  # noqa: F401
load_dotenv()


@shared_task(name="csi.chamados", bind=True, base=ContextTask)
@wrap_cls
class Chamados[T](CsiBot):
    """Empty."""

    def execution(self, *args: T, **kwargs: T) -> None:
        """Empty."""
