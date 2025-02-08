"""Module: capa.

This module defines the capa class, which handles process information extraction and management
within the CrawJUD-Bots application.
"""

import re
import time
from contextlib import suppress
from datetime import datetime

# from memory_profiler import profile
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from ...common import ErroDeExecucao
from ...core import CrawJUD

# # from ...shared import PropertiesCrawJUD

# fp = open("memory_profiler_capa_projudi.log", "+w")


class capa(CrawJUD):  # noqa: N801
    """The capa class extends CrawJUD to handle specific execution tasks related to process.

    information extraction and management.
    """

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        """Initialize the capa instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        super().__init__()
        # PropertiesCrawJUD.kwrgs = kwrgs
        # for key, value in list(kwrgs.items()):
        #     setattr(PropertiesCrawJUD, key, value)

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:
        """Execute the main processing loop, handling each frame of data.

        Raises:
            Exception: If an unexpected error occurs during execution.

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
                self.logger.error(str(e))
                old_message = None
                # windows = self.driver.window_handles

                # if len(windows) == 0:
                #     with suppress(Exception):
                #         self.DriverLaunch(message="Webdriver encerrado inesperadamente, reinicializando...")

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

    def queue(self) -> None:
        """Handle the queue processing, refreshing the driver and extracting process information.

        Raises:
            ErroDeExecucao: If the process is not found or extraction fails.

        """
        try:
            search = self.search_bot()

            if search is not True:
                raise ErroDeExecucao("Processo não encontrado!")

            self.driver.refresh()
            data = self.get_process_informations()
            self.append_success(data, "Informações do processo extraidas com sucesso!")

        except Exception as e:
            self.logger.error(str(e))
            raise ErroDeExecucao(e=e) from e

    def get_process_informations(self) -> list:  # noqa: C901
        """Extract information from the current process in the web driver.

        Returns:
            list: A list of dictionaries containing process information.

        Raises:
            Exception: If an error occurs during information extraction.

        """
        try:
            grau = int(str(self.bot_data.get("GRAU", "1")).replace("º", ""))
            process_info: dict[str, str | int | datetime] = {}
            process_info.update({"NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO")})

            def format_vl_causa(valorDaCausa: str) -> float | str:  # noqa: N803
                """Format the value of the cause by removing currency symbols and converting to float.

                Args:
                    valorDaCausa (str): The raw value string.

                Returns:
                    float | str: The formatted value as float or original string if no match.

                """
                if "¤" in valorDaCausa:
                    valorDaCausa = valorDaCausa.replace("¤", "")  # noqa: N806

                pattern = r"(?<!\S)(?:US\$[\s]?|R\$[\s]?|[\$]?)\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?(?!\S)"
                matches = re.findall(pattern, valorDaCausa)
                if len(matches) > 0:

                    def convert_to_float(value: str) -> float:
                        """Convert a formatted string to float.

                        Args:
                            value (str): The string to convert.

                        Returns:
                            float: The converted float value.

                        """
                        # Remover símbolos de moeda e espaços
                        value = re.sub(r"[^\d.,]", "", value)

                        # Identificar se o formato é BRL (com vírgula para decimais) ou USD (com ponto para decimais)
                        if "," in value and "." in value:
                            # Assumir formato USD se houver tanto ',' quanto '.'
                            parts = value.split(".")
                            if len(parts[-1]) == 2:
                                value = value.replace(",", "")
                            elif not len(parts[-1]) == 2:
                                value = value.replace(".", "").replace(",", ".")
                        elif "," in value:
                            # Assumir formato BRL
                            value = value.replace(".", "").replace(",", ".")
                        elif "." in value:
                            # Assumir formato USD
                            value = value.replace(",", "")

                        return float(value)

                    return convert_to_float(matches[0])

                return valorDaCausa

            self.message = f"Obtendo informações do processo {self.bot_data.get('NUMERO_PROCESSO')}..."
            self.type_log = "log"
            self.prt()

            btn_infogeral = self.driver.find_element(By.CSS_SELECTOR, self.elements.btn_infogeral)
            btn_infogeral.click()

            includecontent: list[WebElement] = []

            element_content = self.elements.primeira_instform1
            element_content2 = self.elements.primeira_instform2

            if grau == 2:
                element_content = self.elements.segunda_instform
                element_content2 = element_content

            includecontent.append(self.driver.find_element(By.CSS_SELECTOR, element_content))
            includecontent.append(self.driver.find_element(By.CSS_SELECTOR, element_content2))

            for incl in includecontent:
                itens = list(
                    filter(
                        lambda x: len(x.find_elements(By.TAG_NAME, "td")) > 1,
                        incl.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr"),
                    ),
                )

                for item in itens:
                    labels = list(
                        filter(
                            lambda x: x.text.strip() != "",
                            item.find_elements(By.CSS_SELECTOR, "td.label, td.labelRadio > label"),
                        ),
                    )
                    # para teste
                    # for value in item.find_elements(By.CSS_SELECTOR, "td"):
                    #     print(value.text.strip())

                    values = list(
                        filter(
                            lambda x: x.text.strip() != "" and not x.get_attribute("class"),
                            item.find_elements(By.TAG_NAME, "td"),
                        ),
                    )

                    for _, label in enumerate(labels):
                        if len(labels) != len(values):
                            continue

                        not_formated_label = label.text
                        label_text = self.format_string(label.text).upper().replace(" ", "_")

                        indice = labels.index(label)
                        value_text = values[indice].text

                        if label_text == "VALOR_DA_CAUSA":
                            value_text = format_vl_causa(value_text)

                        elif "DATA" in label_text or "DISTRIBUICAO" in label_text or "AUTUACAO" in label_text:
                            if " às " in value_text:
                                value_text = value_text.split(" às ")[0]

                            if self.text_is_a_date(value_text) is True:
                                value_text = datetime.strptime(value_text, "%d/%m/%Y")

                        elif not_formated_label != value_text:
                            value_text = " ".join(value_text.split(" ")).upper()

                        else:
                            continue

                        process_info.update({label_text: value_text})

            btn_partes = self.elements.btn_partes
            if grau == 2:
                btn_partes = btn_partes.replace("2", "1")

            btn_partes = self.driver.find_element(By.CSS_SELECTOR, btn_partes)
            btn_partes.click()

            try:
                includecontent = self.driver.find_element(By.ID, self.elements.includecontent_capa)
            except Exception:
                time.sleep(3)
                self.driver.refresh()
                time.sleep(1)
                includecontent = self.driver.find_element(By.ID, self.elements.includecontent_capa)

            result_table = includecontent.find_elements(By.CLASS_NAME, self.elements.resulttable)

            for pos, parte_info in enumerate(result_table):
                h4_name = list(
                    filter(lambda x: x.text != "" and x is not None, includecontent.find_elements(By.TAG_NAME, "h4")),
                )
                tipo_parte = self.format_string(h4_name[pos].text).replace(" ", "_").upper()

                nome_colunas = []

                for column in parte_info.find_element(By.TAG_NAME, "thead").find_elements(By.TAG_NAME, "th"):
                    nome_colunas.append(column.text.upper())

                for parte in parte_info.find_element(By.TAG_NAME, "tbody").find_elements(
                    By.XPATH,
                    self.elements.table_moves,
                ):
                    for pos_, nome_coluna in enumerate(nome_colunas):
                        key = "_".join((self.format_string(nome_coluna).replace(" ", "_").upper(), tipo_parte))
                        value = parte.find_elements(By.TAG_NAME, "td")[pos_].text

                        if value:
                            " ".join(value.split(" "))

                            if "\n" in value:
                                value = " | ".join(value.split("\n"))
                                process_info.update({key: value})
                                continue

                            process_info.update({key: value})

            return [process_info]

        except Exception as e:
            raise e
