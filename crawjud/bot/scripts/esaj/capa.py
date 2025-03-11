"""Manage capa operations and extract process information for CrawJUD-Bots.

This module executes the workflow to search and process process details,
ensuring detailed extraction and logging of information.
"""

import time
import traceback
from contextlib import suppress
from time import sleep
from typing import Self

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.bot.common import ExecutionError
from crawjud.bot.core import CrawJUD


class Capa(CrawJUD):
    """Perform capa tasks by searching and extracting process details robustly.

    This class handles process information retrieval including form extraction
    and logging. It supports multiple process degrees.
    """

    @classmethod
    def initialize(cls, *args: str | int, **kwargs: str | int) -> Self:
        """Initialize a Capa instance with given parameters and settings.

        Args:
            *args (str|int): Positional arguments.
            **kwargs (str|int): Keyword arguments.

        Returns:
            Self: A new instance of Capa.

        """
        return cls(*args, **kwargs)

    def __init__(self, *args: str | int, **kwargs: str | int) -> None:
        """Initialize Capa instance and authenticate the bot for processing.

        Args:
            *args (str|int): Positional arguments.
            **kwargs (str|int): Keyword arguments.

        Side Effects:
            Authenticates the bot and records the start time.

        """
        super().__init__()
        self.module_bot = __name__

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:
        """Execute capa processing by iterating over rows with robust error handling.

        Iterates over the dataframe, renews sessions when expired, and logs errors
        for each process.
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
                self.logger.exception(
                    "".join(
                        traceback.format_exception(
                            etype=type(e),
                            value=e,
                            tb=e.__traceback__,
                        )
                    )
                )
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
        """Queue capa tasks by searching for process data and appending details to logs.

        Calls the search method and retrieves detailed process information.
        """
        try:
            self.search_bot()
            self.append_success(self.get_process_informations())

        except Exception as e:
            self.logger.exception(
                "".join(
                    traceback.format_exception(
                        etype=type(e),
                        value=e,
                        tb=e.__traceback__,
                    )
                )
            )
            raise ExecutionError(e=e) from e

    def get_process_informations(self) -> list:
        """Extract and return detailed process information from the web elements.

        Returns:
            list: A structured list containing process details such as area, forum, and value.

        Note:
            Extraction varies by process degree.

        """
        # chk_advs = ["Advogada", "Advogado"]
        # adv_polo_ativo = "Não consta"
        # adv_polo_passivo = "Não consta"

        self.message = f"Extraindo informações do processo nº{self.bot_data.get('NUMERO_PROCESSO')}"
        self.type_log = "log"
        self.prt()

        grau = int(str(self.bot_data.get("GRAU", "1")).replace("º", ""))

        self.driver.execute_script("$('div#maisDetalhes').show()")

        if grau == 1:
            acao: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.acao)),
            ).text
            area_do_direito = "Diversos"

            if acao == "Procedimento do Juizado Especial Cível":
                area_do_direito = str(acao).replace("Procedimento do ", "")

            subarea_direito = "Geral"
            estado = "Amazonas"
            comarca = self.driver.find_element(By.ID, "foroProcesso").text

            if "Fórum de " in comarca:
                comarca = str(comarca).replace("Fórum de ", "")

            vara: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.vara_processual)),
            ).text.split(" ")[0]
            foro: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.vara_processual)),
            ).text.replace(f"{vara} ", "")

            table_partes = self.driver.find_element(By.ID, self.elements.area_selecao)
            polo_ativo = (
                table_partes.find_elements(By.TAG_NAME, "tr")[0].find_elements(By.TAG_NAME, "td")[1].text.split("\n")[0]
            )

            tipo_parte = "Autor"
            cpf_polo_ativo = "Não consta"

            polo_passivo = (
                table_partes.find_elements(By.TAG_NAME, "tr")[1].find_elements(By.TAG_NAME, "td")[1].text.split("\n")[0]
            )

            tipo_passivo = "réu"
            cpf_polo_passivo = "Não consta"

            try:
                adv_polo_ativo = (
                    table_partes.find_elements(By.TAG_NAME, "tr")[0]
                    .find_elements(By.TAG_NAME, "td")[1]
                    .text.split(":")[1]
                    .replace("Advogado:", "")
                    .replace("Advogada:", "")
                    .replace("  ", "")
                )

            except Exception:
                adv_polo_ativo = "Não consta"
            escritorio_externo = "Fonseca Melo e Viana Advogados Associados"
            fase = "inicial"
            valor = ""
            with suppress(TimeoutException):
                valor: WebElement = (
                    WebDriverWait(self.driver, 1, 0.01)
                    .until(ec.presence_of_element_located((By.ID, self.elements.id_valor)))
                    .text
                )

            def converte_valor_causa(valor_causa: str) -> str:
                if "R$" in valor_causa:
                    valor_causa = float(
                        valor_causa.replace("$", "")
                        .replace("R", "")
                        .replace(" ", "")
                        .replace(".", "")
                        .replace(",", "."),
                    )
                    return f"{valor_causa:.2f}".replace(".", ",")

                if "R$" not in valor_causa:
                    valor_causa = float(valor_causa.replace("$", "").replace("R", "").replace(" ", "").replace(",", ""))
                    return f"{valor_causa:.2f}".replace(".", ",")

            valorDaCausa = valor  # noqa: N806
            if valor != "":
                valorDaCausa = converte_valor_causa(valor)  # noqa: N806

            sleep(0.5)
            distnotformated: WebElement = (
                self.wait.until(ec.presence_of_element_located((By.ID, self.elements.data_processual)))
                .text.replace(" às ", "|")
                .replace(" - ", "|")
            )
            distdata = distnotformated.split("|")[0]
            processo_data = [
                self.bot_data.get("NUMERO_PROCESSO"),
                area_do_direito,
                subarea_direito,
                estado,
                comarca,
                foro,
                vara,
                distdata,
                polo_ativo,
                tipo_parte,
                cpf_polo_ativo,
                polo_passivo,
                tipo_passivo,
                cpf_polo_passivo,
                "",
                "",
                "",
                acao,
                "",
                "",
                "",
                "",
                adv_polo_ativo,
                "",
                escritorio_externo,
                valorDaCausa,
                fase,
            ]

        elif grau == 2:
            data = {"NUMERO_PROCESSO": ""}

            sumary_1_esaj = self.wait.until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, self.elements.sumary_header_1)),
            )

            sumary_2_esaj = self.wait.until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, self.elements.sumary_header_2)),
            )

            list_sumary = [sumary_1_esaj, sumary_2_esaj]

            for pos_, sumary in enumerate(list_sumary):
                for pos, rows in enumerate(sumary):
                    subitems_sumary = rows.find_elements(By.CSS_SELECTOR, self.elements.rows_sumary_)

                    for item in subitems_sumary:
                        if pos == 0 and pos_ == 0:
                            num_proc = item.find_element(By.CLASS_NAME, self.elements.numproc).text
                            status_proc = "Em Andamento"
                            with suppress(NoSuchElementException):
                                status_proc = item.find_element(By.CLASS_NAME, self.elements.statusproc).text

                            data.update({"NUMERO_PROCESSO": num_proc, "STATUS": status_proc.upper()})
                            continue

                        title = item.find_element(By.CLASS_NAME, self.elements.nameitemsumary).text

                        value = item.find_element(By.CLASS_NAME, self.elements.valueitemsumary).text

                        data.update({title.upper(): value.upper()})

            table_partes = self.driver.find_element(By.ID, self.elements.area_selecao)
            for group_parte in table_partes.find_elements(By.TAG_NAME, "tr"):
                pos_repr = 0
                type_parte = self.format_string(group_parte.find_elements(By.TAG_NAME, "td")[0].text.upper())

                info_parte = group_parte.find_elements(By.TAG_NAME, "td")[1]
                info_parte_text = info_parte.text.split("\n")
                if "\n" in info_parte.text:
                    for attr_parte in info_parte_text:
                        if ":" in attr_parte:
                            representante = attr_parte.replace("  ", "").split(":")
                            tipo_representante = representante[0].upper()
                            nome_representante = representante[1].upper()
                            key = {f"{tipo_representante}_{type_parte}": nome_representante}

                            doc_ = "Não consta"
                            with suppress(NoSuchElementException):
                                doc_ = info_parte.find_elements(By.TAG_NAME, "input")[pos_repr]
                                doc_ = doc_.get_attribute("value")

                            key_doc = {f"DOC_{tipo_representante}_{type_parte}": doc_}

                            pos_repr += 1

                            data.update(key)
                            data.update(key_doc)

                        elif ":" not in attr_parte:
                            key = {type_parte: attr_parte}
                            data.update(key)

                elif "\n" not in info_parte_text:
                    key = {type_parte: info_parte.text}
                    data.update(key)

            # polo_ativo = (
            #     table_partes.find_elements(By.TAG_NAME, "tr")[0]
            #     .find_elements(By.TAG_NAME, "td")[1]
            #     .text.split("\n")[0]
            # )
            # adv_polo_ativo = (
            #     table_partes.find_elements(By.TAG_NAME, "tr")[0]
            #     .find_elements(By.TAG_NAME, "td")[-1]
            #     .text.split(":")[1]
            # )

            # if any(chk_adv in adv_polo_ativo for chk_adv in chk_advs):
            #     adv_polo_ativo = adv_polo_ativo.replace("Advogado", "").replace(
            #         "Advogado", ""
            #     )

            # polo_passivo = (
            #     table_partes.find_elements(By.TAG_NAME, "tr")[1]
            #     .find_elements(By.TAG_NAME, "td")[1]
            #     .text.split("\n")[0]
            # )

            # try:
            #     adv_polo_passivo = (
            #         table_partes.find_elements(By.TAG_NAME, "tr")[1]
            #         .find_elements(By.TAG_NAME, "td")[1]
            #         .text.split(":")[1]
            #         .replace("Advogada", "")
            #         .replace("Advogado", "")
            #     )

            # except Exception:
            #     adv_polo_passivo = "Não consta"
            return [data]

        return processo_data
