"""Gerencia tarefas e execução de chamados CSI para automação judicial.

Este módulo define a classe Chamados, responsável por orquestrar tarefas
automatizadas relacionadas a chamados CSI, utilizando integração com bots,
tratamento de contexto e execução assíncrona de tarefas.

"""

from __future__ import annotations

from time import sleep

from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from tqdm import tqdm

from crawjud.controllers.csi import CsiBot
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task, wrap_cls
from crawjud.resources.elements import csi as el

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
