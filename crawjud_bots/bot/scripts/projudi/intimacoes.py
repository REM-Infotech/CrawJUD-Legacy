"""Module: Intimações.

Extract and manage process intimation information from the Projudi system.
"""

import re  # noqa: F401
import time
from contextlib import suppress
from datetime import datetime  # noqa: F401
from typing import Self

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select

from ....common import ExecutionError
from ....core import CrawJUD


class Intimacoes(CrawJUD):
    """Extract and process intimations in Projudi by navigating pages and extracting data.

    This class extends CrawJUD to enter the intimacoes tab, set page sizes,
    and retrieve detailed process intimation information.
    """

    @classmethod
    def initialize(
        cls,
        *args: str | int,
        **kwargs: str | int,
    ) -> Self:
        """Initialize an Intimacoes instance with given parameters.

        Args:
            *args (tuple[str | int]): Positional arguments.
            **kwargs (dict[str, str | int]): Keyword arguments.

        Returns:
            Self: The initialized Intimacoes instance.

        """
        return cls(*args, **kwargs)

    def __init__(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Initialize the Intimacoes instance and authenticate.

        Args:
            *args (tuple[str | int]): Positional arguments.
            **kwargs (dict[str, str | int]): Keyword arguments.

        """
        super().__init__()

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:
        """Execute the intimation extraction loop and handle pagination.

        Iterates through intimation pages and queues extraction of process data.
        """
        self.driver.get(self.elements.url_mesa_adv)
        self.enter_intimacoes()
        self.set_page_size()
        pages_count = self.calculate_pages(self.aba_initmacoes())
        self.total_rows = pages_count
        for i in range(pages_count):
            self.bot_data = {}

            self.bot_data.update({"PID": self.pid, "ROW": i})

            self.row = i + 1
            if self.isStoped:
                break

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth_bot()

            try:
                self.queue()

            except Exception as e:
                self.logger.error(str(e))
                old_message = None
                # windows = self.driver.window_handles

                # if len(windows) == 0:
                #     with suppress(Exception):
                #         self.driver_launch(message="Webdriver encerrado inesperadamente, reinicializando...")

                #     old_message = self.message

                #     self.auth_bot()

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

    def enter_intimacoes(self) -> None:
        """Enter the 'intimações' tab in the Projudi system via script execution."""
        self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.btn_aba_intimacoes)))
        self.driver.execute_script(self.elements.tab_intimacoes_script)
        time.sleep(1)

    def aba_initmacoes(self) -> WebElement:
        """Retrieve the intimações table element for data extraction.

        Returns:
            WebElement: The intimações table element.

        """
        return self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div[id="tabprefix1"]')))

    def set_page_size(self) -> None:
        """Set the page size for the intimacoes table to 100."""
        select = Select(
            self.wait.until(
                ec.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.select_page_size_intimacoes),
                )
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
        info_count = aba_intimacoes.find_element(By.CSS_SELECTOR, 'div[class="navLeft"]').text.split(" ")[0]
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
            self.type_log = "log"
            self.prt()
            name_colunas, intimacoes = self.get_intimacoes(self.aba_initmacoes())
            data = self.get_intimacao_information(name_colunas, intimacoes)
            self.append_success(data, "Intimações extraídas com sucesso!")

            if self.total_rows > 1:
                self.driver.find_element(By.CSS_SELECTOR, 'a[class="arrowNextOn"]').click()

        except Exception as e:
            self.logger.error(str(e))
            raise ExecutionError(e=e) from e

    def get_intimacao_information(self, name_colunas: list[WebElement], intimacoes: list[WebElement]) -> dict:
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
            itens: tuple[str] = tuple(item.find_elements(By.TAG_NAME, "td")[0].text.split("\n"))
            itens2: tuple[str] = tuple(item.find_elements(By.TAG_NAME, "td")[1].text.split("\n"))
            itens3: tuple[str] = tuple(item.find_elements(By.TAG_NAME, "td")[2].text.split("\n"))

            self.message = "Intimação do processo %s encontrada!" % itens[0]
            self.type_log = "log"
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

    def get_intimacoes(self, aba_intimacoes: WebElement) -> tuple[list[WebElement], list[WebElement]]:
        """Retrieve the header and row elements from the intimações table.

        Args:
            aba_intimacoes (WebElement): The intimacoes table element.

        Returns:
            tuple: A tuple containing headers and row elements.

        """
        table_intimacoes = aba_intimacoes.find_element(By.CSS_SELECTOR, 'table[class="resultTable"]')

        thead_table = table_intimacoes.find_element(By.TAG_NAME, "thead").find_elements(By.TAG_NAME, "th")
        tbody_table = table_intimacoes.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

        return thead_table, tbody_table

    # def get_process_informations(self) -> list:
    #     """Extract information from the current process in the web driver.

    #     Returns:
    #         list: A list of dictionaries containing process information.

    #     Raises:
    #         Exception: If an error occurs during information extraction.

    #     """
    #     try:
    #         grau = self.bot_data.get("GRAU", 1)

    #         if grau is None:
    #             grau = 1

    #         if isinstance(grau, str):
    #             grau = grau.strip()

    #         grau = int(grau)
    #         process_info: dict[str, str | int | datetime] = {}
    #         process_info.update({"NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO")})

    #         def format_vl_causa(valor_causa: str) -> float | str:
    #             """Format the value of the cause by removing currency symbols and converting to float.

    #             Args:
    #                 valor_causa (str): The raw value string.

    #             Returns:
    #                 float | str: The formatted value as float or original string if no match.

    #             """
    #             if "¤" in valor_causa:
    #                 valor_causa = valor_causa.replace("¤", "")

    #             pattern = r"(?<!\S)(?:US\$[\s]?|R\$[\s]?|[\$]?)\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?(?!\S)"
    #             matches = re.findall(pattern, valor_causa)
    #             if len(matches) > 0:

    #                 def convert_to_float(value: str) -> float:
    #                     """Convert a formatted string to float.

    #                     Args:
    #                         value (str): The string to convert.

    #                     Returns:
    #                         float: The converted float value.

    #                     """
    #                     # Remover símbolos de moeda e espaços
    #                     value = re.sub(r"[^\d.,]", "", value)

    #                     # Identificar se o formato é BRL (com vírgula para decimais) ou USD (com ponto para decimais)
    #                     if "," in value and "." in value:
    #                         # Assumir formato USD se houver tanto ',' quanto '.'
    #                         parts = value.split(".")
    #                         if len(parts[-1]) == 2:
    #                             value = value.replace(",", "")
    #                         elif not len(parts[-1]) == 2:
    #                             value = value.replace(".", "").replace(",", ".")
    #                     elif "," in value:
    #                         # Assumir formato BRL
    #                         value = value.replace(".", "").replace(",", ".")
    #                     elif "." in value:
    #                         # Assumir formato USD
    #                         value = value.replace(",", "")

    #                     return float(value)

    #                 return convert_to_float(matches[0])

    #             return valor_causa

    #         self.message = f"Obtendo informações do processo {self.bot_data.get('NUMERO_PROCESSO')}..."
    #         self.type_log = "log"
    #         self.prt()

    #         btn_infogeral = self.driver.find_element(By.CSS_SELECTOR, self.elements.btn_infogeral)
    #         btn_infogeral.click()

    #         includecontent: list[WebElement] = []

    #         element_content = self.elements.primeira_instform1
    #         element_content2 = self.elements.primeira_instform2

    #         if grau == 2:
    #             element_content = self.elements.segunda_instform
    #             element_content2 = element_content

    #         includecontent.append(self.driver.find_element(By.CSS_SELECTOR, element_content))
    #         includecontent.append(self.driver.find_element(By.CSS_SELECTOR, element_content2))

    #         for incl in includecontent:
    #             itens = list(
    #                 filter(
    #                     lambda x: len(x.find_elements(By.TAG_NAME, "td")) > 1,
    #                     incl.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr"),
    #                 ),
    #             )

    #             for item in itens:
    #                 labels = list(
    #                     filter(
    #                         lambda x: x.text.strip() != "",
    #                         item.find_elements(By.CSS_SELECTOR, "td.label, td.labelRadio > label"),
    #                     ),
    #                 )
    #                 # para teste
    #                 # for value in item.find_elements(By.CSS_SELECTOR, "td"):
    #                 #     print(value.text.strip())

    #                 values = list(
    #                     filter(
    #                         lambda x: x.text.strip() != "" and not x.get_attribute("class"),
    #                         item.find_elements(By.TAG_NAME, "td"),
    #                     ),
    #                 )

    #                 for _, label in enumerate(labels):
    #                     if len(labels) != len(values):
    #                         continue

    #                     not_formated_label = label.text
    #                     label_text = self.format_string(label.text).upper().replace(" ", "_")

    #                     indice = labels.index(label)
    #                     value_text = values[indice].text

    #                     if label_text == "VALOR_DA_CAUSA":
    #                         value_text = format_vl_causa(value_text)

    #                     elif "DATA" in label_text or "DISTRIBUICAO" in label_text or "AUTUACAO" in label_text:
    #                         if " às " in value_text:
    #                             value_text = value_text.split(" às ")[0]

    #                         if self.text_is_a_date(value_text) is True:
    #                             value_text = datetime.strptime(value_text, "%d/%m/%Y")

    #                     elif not_formated_label != value_text:
    #                         value_text = " ".join(value_text.split(" ")).upper()

    #                     else:
    #                         continue

    #                     process_info.update({label_text: value_text})

    #         btn_partes = self.elements.btn_partes
    #         if grau == 2:
    #             btn_partes = btn_partes.replace("2", "1")

    #         btn_partes = self.driver.find_element(By.CSS_SELECTOR, btn_partes)
    #         btn_partes.click()

    #         try:
    #             includecontent = self.driver.find_element(By.ID, self.elements.includecontent_capa)
    #         except Exception:
    #             time.sleep(3)
    #             self.driver.refresh()
    #             time.sleep(1)
    #             includecontent = self.driver.find_element(By.ID, self.elements.includecontent_capa)

    #         result_table = includecontent.find_elements(By.CLASS_NAME, self.elements.resulttable)

    #         for pos, parte_info in enumerate(result_table):
    #             h4_name = list(
    #                 filter(lambda x: x.text != "" and x is not None, includecontent.find_elements(By.TAG_NAME, "h4")),
    #             )
    #             tipo_parte = self.format_string(h4_name[pos].text).replace(" ", "_").upper()

    #             nome_colunas = []

    #             for column in parte_info.find_element(By.TAG_NAME, "thead").find_elements(By.TAG_NAME, "th"):
    #                 nome_colunas.append(column.text.upper())

    #             for parte in parte_info.find_element(By.TAG_NAME, "tbody").find_elements(
    #                 By.XPATH,
    #                 self.elements.table_moves,
    #             ):
    #                 for pos_, nome_coluna in enumerate(nome_colunas):
    #                     key = "_".join((self.format_string(nome_coluna).replace(" ", "_").upper(), tipo_parte))
    #                     value = parte.find_elements(By.TAG_NAME, "td")[pos_].text

    #                     if value:
    #                         " ".join(value.split(" "))

    #                         if "\n" in value:
    #                             value = " | ".join(value.split("\n"))
    #                             process_info.update({key: value})
    #                             continue

    #                         process_info.update({key: value})

    #         return [process_info]

    #     except Exception as e:
    #         raise e
