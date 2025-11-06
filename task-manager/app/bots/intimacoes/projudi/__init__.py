"""Module: Intimações.

Extract and manage process intimation information from the Projudi system.
"""

import time
from contextlib import suppress

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select

from app.common.exceptions import ExecutionError
from app.controllers.projudi import ProjudiBot
from app.resources.driver.web_element import (
    WebElementBot as WebElement,
)
from app.resources.elements import projudi as el


class Intimacoes(ProjudiBot):
    """Extract and process intimations in Projudi by navigating pages and extracting data.

    This class extends CrawJUD to enter the intimacoes tab, set page sizes,
    and retrieve detailed process intimation information.
    """

    def execution(self) -> None:
        """Execute the intimation extraction loop and handle pagination.

        Iterates through intimation pages and queues extraction of process data.
        """
        self.driver.get(el.url_mesa_adv)
        self.enter_intimacoes()
        self.set_page_size()
        pages_count = self.calculate_pages(self.aba_initmacoes())
        self.total_rows = pages_count
        for i in range(pages_count):
            self.bot_data = {}

            self.bot_data.update({"PID": self.pid, "ROW": i})

            self.row = i + 1

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth()

            try:
                self.queue()

            except ExecutionError as e:
                message_error = str(e)

                self.print_message(
                    message=f"{message_error}.",
                    message_type="error",
                )

                self.bot_data.update({"MOTIVO_ERRO": message_error})
                self.append_error(data_save=[self.bot_data])

        self.finalizar_execucao()

    def enter_intimacoes(self) -> None:
        """Enter the 'intimações' tab in the Projudi system via script execution."""
        self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.btn_aba_intimacoes,
            )),
        )
        self.driver.execute_script(el.tab_intimacoes_script)
        time.sleep(1)

    def aba_initmacoes(self) -> WebElement:
        """Retrieve the intimações table element for data extraction.

        Returns:
            WebElement: The intimações table element.

        """
        return self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'div[id="tabprefix1"]',
            )),
        )

    def set_page_size(self) -> None:
        """Set the page size for the intimacoes table to 100."""
        select = Select(
            self.wait.until(
                ec.presence_of_element_located(
                    (By.CSS_SELECTOR, el.select_page_size_intimacoes),
                ),
            ),
        )
        select.select_by_value("100")

    def calculate_pages(self, aba_intimacoes: WebElement) -> int:
        """Calculate the total number of intimation pages using table info.

        Args:
            aba_intimacoes (WebElement): The intimacoes table element.

        Returns:
            int: The total number of pages.

        """
        info_count = aba_intimacoes.find_element(
            By.CSS_SELECTOR,
            'div[class="navLeft"]',
        ).text.split(" ")[0]
        info_count = int(info_count)
        calculate = info_count // 100

        if calculate > 1.0:
            if info_count % 100 > 0:
                calculate += 1

            return int(calculate)

        return 1

    def queue(self) -> None:
        """Handle the intimation extraction queue and advance pagination.

        Raises:
            ExecutionError: If extraction or navigation fails.

        """
        try:
            self.message = "Buscando intimações..."
            self.message_type = "log"
            self.prt()
            name_colunas, intimacoes = self.get_intimacoes(
                self.aba_initmacoes(),
            )
            data = self.get_intimacao_information(
                name_colunas,
                intimacoes,
            )
            self.append_success(
                data,
                "Intimações extraídas com sucesso!",
            )

            if self.total_rows > 1:
                self.driver.find_element(
                    By.CSS_SELECTOR,
                    'a[class="arrowNextOn"]',
                ).click()

        except ExecutionError as e:
            raise ExecutionError(exc=e) from e

    def get_intimacao_information(
        self,
        name_colunas: list[WebElement],
        intimacoes: list[WebElement],
    ) -> dict:
        """Extract detailed intimation information from table rows.

        Args:
            name_colunas (list[WebElement]): Table header elements.
            intimacoes (list[WebElement]): Table row elements for intimations.

        Returns:
            dict: Processed intimation data.

        """
        list_data = []
        for item in intimacoes:
            data: dict[str, str] = {}
            itens: tuple[str] = tuple(
                item.find_elements(By.TAG_NAME, "td")[0].text.split(
                    "\n",
                ),
            )
            itens2: tuple[str] = tuple(
                item.find_elements(By.TAG_NAME, "td")[1].text.split(
                    "\n",
                ),
            )
            itens3: tuple[str] = tuple(
                item.find_elements(By.TAG_NAME, "td")[2].text.split(
                    "\n",
                ),
            )

            self.message = f"Intimação do processo {itens[0]} encontrada!"
            self.message_type = "log"
            self.prt()

            with suppress(IndexError):
                data["NUMERO_PROCESSO"] = itens[0]
                data["PARTE_INTIMADA"] = itens[1]
                data["VARA"] = itens[2]

            with suppress(IndexError):
                data["EVENTO"] = itens2[0]
                data["PRAZO"] = itens2[1]

            with suppress(IndexError):
                data["DATA_ENVIO"] = itens3[0].strip()
                data["ULTIMO_DIA"] = itens3[1].strip()

            list_data.append(data)

        return list_data

    def get_intimacoes(
        self,
        aba_intimacoes: WebElement,
    ) -> tuple[list[WebElement], list[WebElement]]:
        """Retrieve the header and row elements from the intimações table.

        Args:
            aba_intimacoes (WebElement): The intimacoes table element.

        Returns:
            tuple: A tuple containing headers and row elements.

        """
        table_intimacoes = aba_intimacoes.find_element(
            By.CSS_SELECTOR,
            'table[class="resultTable"]',
        )

        thead_table = table_intimacoes.find_element(
            By.TAG_NAME,
            "thead",
        ).find_elements(By.TAG_NAME, "th")
        tbody_table = table_intimacoes.find_element(
            By.TAG_NAME,
            "tbody",
        ).find_elements(By.TAG_NAME, "tr")

        return thead_table, tbody_table
