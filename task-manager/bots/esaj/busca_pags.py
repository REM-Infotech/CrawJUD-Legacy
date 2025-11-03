"""Module: busca_pags.

This module manages page search operations for paid costs in the CrawJUD-Bots app.
"""

from contextlib import suppress
from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from bots.esaj.master import ESajBot
from common.exceptions import ExecutionError
from resources.elements import esaj as el

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement


class BuscaPags(ESajBot):
    """Class BuscaPags.

    Manages page search and the extraction of cost-related information.

    Attributes:
        datetimeNOW (str): The current datetime in "America/Manaus" timezone.


    Methods:
        initialize: Create a new BuscaPags instance.
        execution: Run the page search loop.
        queue: Retrieve and process the paid costs page.
        get_page_custas_pagas: Navigate to the paid costs page.
        page_custas: Extract cost details from the paid costs table.

    """

    def execution(self) -> None:
        """Execute page search.

        Iterates over each data row, checks session status, and logs errors.

        # Inline: For each row, execute the queue sequence.
        """
        frame = self.frame
        self.total_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value

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

        self.finalize_execution()

    def queue(self) -> None:
        """Queue page search tasks.

        Retrieves the paid costs page and processes cost data.

        Raises:
            ExecutionError: Propagates errors encountered during page search.

        """
        try:
            self.get_page_custas_pagas()
            self.page_custas()

        except ExecutionError as e:
            raise ExecutionError(exc=e) from e

    def get_page_custas_pagas(self) -> None:
        """Retrieve the paid costs page.

        Extracts the URL from the element and navigates to it.

        # Inline: Use Selenium to get the onclick attribute and redirect.
        """
        generatepdf = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.get_page_custas_pagas,
            )),
        )
        onclick_value = generatepdf.get_attribute("onclick")
        url_start = onclick_value.find("'") + 1
        url_end = onclick_value.find("'", url_start)
        url = onclick_value[url_start:url_end]
        self.driver.get(url)

    def page_custas(self) -> None:
        """Process the paid costs page.

        Extract cost details from tables and append success records.
        """
        divcustaspagas: list[WebElement] = self.wait.until(
            ec.presence_of_all_elements_located((By.TAG_NAME, "div")),
        )
        total = 0
        for divcorreta in divcustaspagas:
            nomediv = None

            with suppress(Exception):
                nomediv = divcorreta.find_element(
                    By.CLASS_NAME,
                    "tituloGridCustas",
                ).text

            if nomediv is None:
                continue

            if "Lista de custas pagas" in nomediv:
                self.message = "Extraindo dados..."
                self.message_type = "log"
                self.prt()

                find_table_pgmt = divcorreta.find_element(
                    By.CSS_SELECTOR,
                    'table[class="spwTabelaGrid"]',
                )

                tr_rows = find_table_pgmt.find_elements(By.TAG_NAME, "tr")
                self.roleta = 0

                for rows in tr_rows:
                    with suppress(Exception):
                        checkifclass = rows.get_attribute("class")
                        if checkifclass == "":
                            tipo_custa = rows.find_elements(By.TAG_NAME, "td")[
                                0
                            ].text
                            emissor = rows.find_elements(By.TAG_NAME, "td")[
                                1
                            ].text
                            data_calculo = str(
                                rows.find_elements(By.TAG_NAME, "td")[2].text,
                            )

                            data_calculo = datetime.strptime(
                                data_calculo,
                                "%d/%m/%Y",
                            ).replace(tzinfo=ZoneInfo("America/Manaus"))

                            valor_custa = (
                                str(
                                    rows.find_elements(By.TAG_NAME, "td")[
                                        3
                                    ].text,
                                )
                                .replace(".", "")
                                .replace(",", ".")
                            )

                            valor_custa = float(valor_custa)

                            cód_guia = str(
                                rows.find_elements(By.TAG_NAME, "td")[4].text,
                            )
                            parcelaguia = rows.find_elements(
                                By.TAG_NAME,
                                "td",
                            )[5].text

                            data_pagamento = str(
                                rows.find_elements(By.TAG_NAME, "td")[6].text,
                            )

                            data_pagamento = datetime.strptime(
                                data_pagamento,
                                "%d/%m/%Y",
                            ).replace(tzinfo=ZoneInfo("America/Manaus"))

                            total += valor_custa

                            self.roleta = self.roleta + 1
                            data = [
                                self.bot_data.get("NUMERO_PROCESSO"),
                                tipo_custa,
                                emissor,
                                data_calculo,
                                valor_custa,
                                cód_guia,
                                parcelaguia,
                                data_pagamento,
                            ]
                            self.append_success()
                        elif checkifclass != "":
                            continue

                        continue

                    tipo_custa = rows.find_elements(By.TAG_NAME, "td")[0].text
                    emissor = rows.find_elements(By.TAG_NAME, "td")[1].text
                    data_calculo = str(
                        rows.find_elements(By.TAG_NAME, "td")[2].text,
                    )

                    data_calculo = datetime.strptime(
                        data_calculo,
                        "%d/%m/%Y",
                    ).replace(tzinfo=ZoneInfo("America/Manaus"))

                    valor_custa = str(
                        rows.find_elements(By.TAG_NAME, "td")[3].text,
                    )

                    valor_custa = float(valor_custa)

                    cód_guia = str(
                        rows.find_elemens(By.TAG_NAME, "td")[4].text,
                    )
                    parcelaguia = rows.find_elements(By.TAG_NAME, "td")[5].text
                    data_pagamento = datetime.strptime(
                        str(rows.find_elements(By.TAG_NAME, "td")[6].text),
                    ).replace(tzinfo=ZoneInfo("America/Manaus"))

                    data_pagamento = datetime.strptime(
                        data_pagamento,
                        "%d/%m/%Y",
                    ).replace(tzinfo=ZoneInfo("America/Manaus"))
                    self.roleta = self.roleta + 1
                    total += valor_custa

                    data = [
                        self.bot_data.get("NUMERO_PROCESSO"),
                        tipo_custa,
                        emissor,
                        data_calculo,
                        valor_custa,
                        cód_guia,
                        parcelaguia,
                        data_pagamento,
                    ]
                    self.append_success(data)

            elif "Lista de custas pagas" not in nomediv:
                continue

            file_name_save = f"Total - {self.pid} - {self.datetimeNOW}.xlsx"
            self.append_success(
                [self.bot_data.get("NUMERO_PROCESSO"), total],
                file_name_save=file_name_save,
            )
