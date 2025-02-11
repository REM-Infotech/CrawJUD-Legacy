"""Module: pje.pauta.

This module fetches and processes court hearing schedules (pautas).
"""

import os
import time
from contextlib import suppress
from datetime import datetime
from time import sleep

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec

from ...common import ExecutionError
from ...core import CrawJUD

# from typing import type


class pauta(CrawJUD):  # noqa: N801
    """Represents the main class to retrieve hearing data (pautas)."""

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        """Initialize the pauta class with any given arguments."""
        super().__init__()
        # PropertiesCrawJUD.kwargs = kwargs
        # for key, value in list(kwargs.items()):
        #     setattr(PropertiesCrawJUD, key, value)

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:
        """Run the main execution logic for retrieving pautas."""
        frame = self.dataFrame()
        self.max_rows = len(frame)

        self.row = 2
        self.current_date = self.data_inicio

        while not self.isStoped and self.current_date <= self.data_fim:
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
        """Process each vara (court branch) in the queue and fetch data about pautas."""
        try:
            self.message = f"Buscando pautas na data {self.current_date.strftime('%d/%m/%Y')}"
            self.type_log = "log"
            self.prt()
            varas: list[str] = self.varas
            for vara in varas:
                date = self.current_date.strftime("%Y-%m-%d")
                self.data_append.update({vara: {date: []}})

                self.driver.get(f"{self.elements.url_pautas}{vara}-{date}")
                self.get_pautas(date, vara)

                data_append = self.data_append[vara][date]
                if len(data_append) == 0:
                    self.data_append[vara].pop(date)

                elif len(data_append) > 0:
                    vara = vara.replace("#", "").upper()
                    fileN = f"{vara} - {date.replace('-', '.')} - {self.pid}.xlsx"  # noqa: N806
                    self.append_success(data=data_append, fileN=fileN)

            data_append = self.group_date_all(self.data_append)
            fileN = os.path.basename(self.path)  # noqa: N806
            if len(data_append) > 0:
                self.append_success(data=[data_append], fileN=fileN, message="Dados extraídos com sucesso!")

            elif len(data_append) == 0:
                self.message = "Nenhuma pauta encontrada"
                self.type_log = "error"
                self.prt()

        except Exception as e:
            raise ExecutionError(e=e) from e

    def get_pautas(self, current_date: type[datetime], vara: str) -> None:
        """Get and parse pautas from the appropriate page.

        Args:
            current_date (datetime): The date for retrieving pautas.
            vara (str): The vara (court branch).

        """
        try:
            # Interage com a tabela de pautas
            self.driver.implicitly_wait(10)
            times = 4
            itens_pautas = None
            table_pautas: WebElement = self.wait.until(
                ec.all_of(ec.presence_of_element_located((By.CSS_SELECTOR, 'pje-data-table[id="tabelaResultado"]'))),
                (ec.visibility_of_element_located((By.CSS_SELECTOR, 'table[name="Tabela de itens de pauta"]'))),
            )[-1]

            with suppress(NoSuchElementException, TimeoutException):
                itens_pautas = table_pautas.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

            # Caso encontre a tabela, raspa os dados
            if itens_pautas:
                self.message = "Pautas encontradas!"
                self.type_log = "log"
                self.prt()

                times = 6

                for item in itens_pautas:
                    vara_name = self.driver.find_element(
                        By.CSS_SELECTOR,
                        'span[class="ng-tns-c11-1 ng-star-inserted"]',
                    ).text
                    with suppress(StaleElementReferenceException):
                        item: WebElement = item
                        itens_tr = item.find_elements(By.TAG_NAME, "td")

                        appends = {
                            "INDICE": int(itens_tr[0].text),
                            "VARA": vara_name,
                            "HORARIO": itens_tr[1].text,
                            "TIPO": itens_tr[2].text,
                            "ATO": itens_tr[3].find_element(By.TAG_NAME, "a").text.split(" ")[0],
                            "NUMERO_PROCESSO": itens_tr[3].find_element(By.TAG_NAME, "a").text.split(" ")[1],
                            "PARTES": itens_tr[3]
                            .find_element(By.TAG_NAME, "span")
                            .find_element(By.TAG_NAME, "span")
                            .text,
                            "SALA": itens_tr[5].text,
                            "SITUACAO": itens_tr[6].text,
                        }

                        self.data_append[vara][current_date].append(appends)
                        self.message = f"Processo {appends['NUMERO_PROCESSO']} adicionado!"
                        self.type_log = "log"
                        self.prt()

                try:
                    btn_next = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Próxima página"]')

                    buttondisabled = btn_next.get_attribute("disabled")
                    if not buttondisabled:
                        btn_next.click()
                        self.get_pautas(current_date, vara)

                except Exception as e:
                    raise ExecutionError(e) from e

            elif not itens_pautas:
                times = 1
            # Eu defini um timer, um caso encontre a tabela e outro
            # para caso não encontre ela

            sleep(times)

        except Exception as e:
            raise ExecutionError(e=e) from e
