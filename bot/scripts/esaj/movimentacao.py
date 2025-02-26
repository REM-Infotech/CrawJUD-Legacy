"""Module: movimentacao.

This module manages movement operations on the Esaj system using the CrawJUD framework.
"""

import time
from contextlib import suppress
from datetime import datetime
from time import sleep
from typing import Self

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec

from ...common import ExecutionError
from ...core import CrawJUD


class Movimentacao(CrawJUD):
    """Class Movimentacao.

    Handles all movement-related tasks in the Esaj system.

    Attributes:
        start_time (float): Timestamp when movements begin processing.
        appends (list): Collection of movement records.


    Methods:
        initialize: Create a new Movimentacao instance.
        execution: Iterate over process rows and process movements.
        queue: Queue tasks for retrieving and appending movements.
        get_moves: Extract movement information from page elements.

    """

    @classmethod
    def initialize(cls, *args: str | int, **kwargs: str | int) -> Self:
        """Initialize a new Movimentacao instance.

        Args:
            *args (str | int): Variable arguments.
            **kwargs (str | int): Keyword arguments.

        Returns:
            Self: A new Movimentacao instance.

        # Inline: Directly return an instance with given arguments.

        """
        return cls(*args, **kwargs)

    def __init__(self, *args: str | int, **kwargs: str | int) -> None:
        """Construct the Movimentacao instance.

        Sets up the crawler by configuring authentication and environment.

        Args:
            *args: Positional arguments for setup.
            **kwargs: Keyword arguments for configuration.

        # Inline: Leverage parent classes for setup and authentication.

        """
        super().__init__()

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:
        """Execute movement processing.

        Iterates over each process row, handling session renewal and error logging.

        Raises:
            ExecutionError: If any movement processing error occurs.

        # Inline: Loop through dataFrame and execute queued movement tasks.

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
                        self.driver_launch(message="Webdriver encerrado inesperadamente, reinicializando...")

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
        """Queue movement tasks.

        Retrieves movement data and appends the results.

        Raises:
            ExecutionError: If the process is not found or movement data errors.

        # Inline: Check for process existence and then extract moves.

        """
        try:
            self.appends = []
            self.resultados = []
            search = bool(self.search_bot())

            if search is True:
                self.get_moves()
                self.append_moves()

            elif search is False:
                raise ExecutionError("Processo não encontrado!")

        except Exception as e:
            raise ExecutionError(e=e) from e

    def get_moves(self) -> None:
        """Retrieve movement information.

        Extracts and appends movement details from the page elements.

        # Inline: Scroll to element, reveal table, then iterate through rows.
        """
        show_all: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, 'a[id="linkmovimentacoes"]')),
        )

        self.interact.scroll_to(show_all)

        # Rolar até o elemento
        self.driver.execute_script("arguments[0].scrollIntoView(true);", show_all)

        # Use JavaScript para clicar no elemento
        self.driver.execute_script("arguments[0].click();", show_all)

        sleep(0.5)

        try:
            table_moves = self.driver.find_element(By.CSS_SELECTOR, self.elements.movimentacoes)
            self.driver.execute_script('document.querySelector("#tabelaTodasMovimentacoes").style.display = "block"')

        except Exception:
            table_moves = self.driver.find_element(By.ID, self.elements.ultimas_movimentacoes)
            self.driver.execute_script('document.querySelector("#tabelaUltimasMovimentacoes").style.display = "block"')

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
                            data_mov = datetime.strptime(data_mov.replace("/", "-"), "%d-%m-%Y")

                    name_mov = mov.split("\n")[0]
                    text_mov = td_tr[2].find_element(By.TAG_NAME, "span").text
                    self.appends.append([self.bot_data.get("NUMERO_PROCESSO"), data_mov, name_mov, text_mov, "", ""])
