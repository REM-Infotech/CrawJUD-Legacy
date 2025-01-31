"""
Module: movimentacao.

This module manages movement-related functionalities within the Esaj system of the CrawJUD-Bots application.
Handles the tracking and processing of case movements, including updating statuses and logging activities.
"""

import time
from contextlib import suppress
from datetime import datetime
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from ...common import ErroDeExecucao
from ...core import CrawJUD

# from ...shared import PropertiesCrawJUD


class Movimentacao(CrawJUD):
    """
    Handles movement-related tasks within the Esaj system.

    Inherits from CrawJUD to utilize core functionalities for processing case movements.

    Attributes:
        start_time (float): Timestamp marking the start of execution.
        max_rows (int): Total number of rows to process.
        row (int): Current row being processed.
        bot_data (dict): Data associated with the current bot operation.
        isStoped (bool): Flag indicating if the execution should stop.
    """

    def __init__(self, *args, **kwrgs) -> None:
        """
        Initialize the Movimentacao instance.

        Sets up the bot by initializing the parent class, configuring settings, and authenticating.

        Args:
            *args: Variable length argument list.
            **kwrgs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwrgs)

        # PropertiesCrawJUD.kwrgs = kwrgs
        # for key, value in list(kwrgs.items()):
        #     setattr(PropertiesCrawJUD, key, value)

        super().setup()
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:
        """
        Execute the movement processing.

        Iterates through each entry in the data frame, managing the execution flow,
        handling session expirations, and logging any errors that occur during processing.

        Raises:
            ErroDeExecucao: If an unexpected error occurs during execution.
        """
        frame = self.dataFrame()
        self.max_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value
            if self.isStoped:
                break

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth_bot()

            try:
                self.queue()

            except Exception as e:
                old_message = None
                windows = self.driver.window_handles

                if len(windows) == 0:
                    with suppress(Exception):
                        self.DriverLaunch(
                            message="Webdriver encerrado inesperadamente, reinicializando..."
                        )

                    old_message = self.message

                    self.auth_bot()

                if old_message is None:
                    old_message = self.message
                message_error = str(e)

                self.type_log = "error"
                self.message_error = f"{message_error}. | Operação: {old_message}"
                self.prt()

                self.bot_data.update({"MOTIVO_ERRO": self.message_error})
                self.append_error(self.bot_data)

                self.message_error = None

        self.finalize_execution()

    def queue(self) -> None:
        """
        Queue the tasks for processing movements.

        Manages the sequence of actions required to process movements, including
        searching for the bot and retrieving movement information.

        Raises:
            ErroDeExecucao: If an error occurs during task queuing.
        """
        try:
            self.appends = []
            self.resultados = []
            search = bool(self.search_bot())

            if search is True:
                self.get_moves()
                self.append_moves()

            elif search is False:
                raise ErroDeExecucao("Processo não encontrado!")

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def get_moves(self) -> None:
        """
        Retrieve movement information.

        Extracts and processes movement-related data from the Esaj system, updating
        the relevant records and logging the activities.

        Raises:
            ErroDeExecucao: If an error occurs while retrieving movement information.
        """
        show_all: WebElement = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[id="linkmovimentacoes"]')
            )
        )

        self.interact.scroll_to(show_all)

        # Rolar até o elemento
        self.driver.execute_script("arguments[0].scrollIntoView(true);", show_all)

        # Use JavaScript para clicar no elemento
        self.driver.execute_script("arguments[0].click();", show_all)

        sleep(0.5)

        try:
            table_moves = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.movimentacoes
            )
            self.driver.execute_script(
                'document.querySelector("#tabelaTodasMovimentacoes").style.display = "block"'
            )

        except Exception:
            table_moves = self.driver.find_element(
                By.ID, self.elements.ultimas_movimentacoes
            )
            self.driver.execute_script(
                'document.querySelector("#tabelaUltimasMovimentacoes").style.display = "block"'
            )

        itens = table_moves.find_elements(By.TAG_NAME, "tr")

        palavra_chave = str(self.bot_data.get("PALAVRA_CHAVE"))
        termos = [palavra_chave]

        if "," in palavra_chave:
            termos = palavra_chave.replace(", ", ",").split(",")

        for termo in termos:
            self.message = f'Buscando movimentações que contenham "{termo}"'
            self.type_log = "log"

            for item in itens:
                td_tr = item.find_elements(By.TAG_NAME, "td")
                mov = td_tr[2].text

                if termo.lower() in mov.lower():
                    data_mov = td_tr[0].text

                    with suppress(Exception):
                        if type(data_mov) is str:
                            data_mov = datetime.strptime(
                                data_mov.replace("/", "-"), "%d-%m-%Y"
                            )

                    name_mov = mov.split("\n")[0]
                    text_mov = td_tr[2].find_element(By.TAG_NAME, "span").text
                    self.appends.append(
                        [
                            self.bot_data.get("NUMERO_PROCESSO"),
                            data_mov,
                            name_mov,
                            text_mov,
                            "",
                            "",
                        ]
                    )
