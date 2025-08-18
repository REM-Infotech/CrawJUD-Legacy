"""Gerencia tarefas e execução de chamados CSI para automação judicial.

Este módulo define a classe Chamados, responsável por orquestrar tarefas
automatizadas relacionadas a chamados CSI, utilizando integração com bots,
tratamento de contexto e execução assíncrona de tarefas.

"""

from __future__ import annotations

import secrets  # noqa: F401
import traceback  # noqa: F401
from contextlib import suppress  # noqa: F401
from threading import Thread  # noqa: F401
from time import sleep
from typing import TYPE_CHECKING, ClassVar  # noqa: F401

from dotenv import load_dotenv
from httpx import Client  # noqa: F401
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from tqdm import tqdm

from crawjud.bots.controllers.csi import CsiBot
from crawjud.bots.controllers.pje import PjeBot  # noqa: F401
from crawjud.bots.resources.elements import csi as el
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
        tqdm.write("OK")

        frame = self.frame

        calls = {
            "Solicitação de Subsídios para Contestação": self.solicitacao_subsidios,
        }

        for pos, item in tqdm(enumerate(frame)):
            self.bot_data = item
            self.row = pos + 1

            func = calls[item["NOME_EVENTO"]]
            func()

        self.driver.quit()

    def solicitacao_subsidios(self) -> None:
        driver = self.driver
        wait = self.wait

        driver.get(el.url_solicitacao_subsidios)

        campo_nome_reclamante = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.campo_nome_reclamante_subsidios,
            )),
        )

        campo_nome_reclamante.send_keys(self.bot_data["AUTOR"])

        sleep(60)
