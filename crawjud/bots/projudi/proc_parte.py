"""Module: proc_parte.

Manage participant processing in the Projudi system by interacting with process lists and varas.
"""

from __future__ import annotations

from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING

from selenium.common.exceptions import (
    NoSuchElementException,
)
from selenium.webdriver.common.by import By

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.projudi import ProjudiBot
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task
from crawjud.decorators.bot import wrap_cls
from crawjud.resources.elements import projudi as el

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement


@shared_task(name="projudi.busca_parte", bind=True, base=ContextTask)
@wrap_cls
class ProcParte(ProjudiBot):
    """Handle participant processing in Projudi with detailed queue management and error handling.

    This class extends CrawJUD to retrieve process lists, store participant information,
    and manage queue execution for the Projudi system.
    """

    def execution(self) -> None:
        """Execute the main loop for participant processing continuously.

        Continuously process queues until stopping, while handling session expirations and errors.
        """
        self.graphicMode = "bar"
        while not self.isStoped:
            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth()

            try:
                self.queue()

            except ExecutionError as e:
                old = self.message
                message_error = str(e)

                self.type_log = "error"
                self.message_error = f"{message_error}. | Operação: {old}"
                self.prt()

                self.bot_data.update({"MOTIVO_ERRO": message_error})
                self.append_error(self.bot_data)

                self.message_error = None

        self.finalize_execution()

    def queue(self) -> None:
        """Manage the participant processing queue and handle varas search."""
        try:
            for vara in self.varas:
                self.vara: str = vara
                search = self.search()
                if search is True:
                    self.get_process_list()

                with suppress(Exception):
                    if self.driver.title.lower() == "a sessao expirou":
                        self.auth()

        except ExecutionError as e:
            message_error = str(e)

            self.print_msg(message=f"{message_error}.", type_log="error")

            self.bot_data.update({"MOTIVO_ERRO": message_error})
            self.append_error(self.bot_data)

            self.message_error = None
            self.queue()

    def get_process_list(self) -> None:
        """Retrieve and process the list of processes from the web interface.

        Extracts process data, manages pagination, and stores the retrieved information.

        Raises:
            ExecutionError: Erro de execução

        """
        try:
            table_processos = self.driver.find_element(
                By.CLASS_NAME,
                "resultTable",
            ).find_element(By.TAG_NAME, "tbody")

            list_processos = None
            next_page = None
            with suppress(NoSuchElementException):
                list_processos = table_processos.find_elements(
                    By.XPATH,
                    './/tr[contains(@class, "odd") or contains(@class, "even")]',
                )

            if list_processos and not self.isStoped:
                self.use_list_process(list_processos)

                with suppress(NoSuchElementException):
                    next_page = self.driver.find_element(
                        By.CLASS_NAME,
                        "navRight",
                    ).find_element(
                        By.XPATH,
                        el.exception_arrow,
                    )

                self.type_log = "info"
                self.append_success(
                    self.data_append,
                    "Processos salvos na planilha!",
                    file_name_save=Path(self.path).name,
                )
                if next_page:
                    next_page.click()
                    self.get_process_list()

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth()

        except ExecutionError as e:
            raise ExecutionError(exc=e) from e

    def use_list_process(self, list_processos: list[WebElement]) -> None:
        """Extract and log details from each process element in the provided list.

        Args:
            list_processos (list[WebElement]): List of process web elements.

        """
        self.data_append.clear()
        for processo in list_processos:
            numero_processo = processo.find_elements(By.TAG_NAME, "td")[1].text

            polo_ativo = "Não consta ou processo em sigilo"
            polo_passivo = "Não consta ou processo em sigilo"
            juizo = "Não consta ou processo em sigilo"

            numero = "".join(filter(str.isdigit, numero_processo))
            anoref = ""
            if numero:
                anoref = numero_processo.split(".")[1]

            with suppress(Exception):
                polo_ativo = (
                    processo.find_elements(By.TAG_NAME, "td")[2]
                    .find_elements(By.TAG_NAME, "td")[1]
                    .text
                )

            with suppress(Exception):
                polo_passivo = processo.find_elements(By.TAG_NAME, "td")[7].text

            with suppress(Exception):
                juizo = processo.find_elements(By.TAG_NAME, "td")[9].text

            self.data_append.append(
                {
                    "NUMERO_PROCESSO": numero_processo,
                    "ANO_REFERENCIA": anoref,
                    "POLO_ATIVO": polo_ativo,
                    "POLO_PASSIVO": polo_passivo,
                    "JUIZO": juizo,
                },
            )
            self.row += 1
            self.message = f"Processo {numero_processo} salvo!"
            self.type_log = "success"
            self.prt()
