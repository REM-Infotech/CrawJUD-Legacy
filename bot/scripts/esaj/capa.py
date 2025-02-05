"""Module: capa.

This module manages the 'capa' functionalities within the CrawJUD-Bots application.
Handles tasks related to document processing, authentication, and error handling within the 'capa' context.
"""

import time
from contextlib import suppress
from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.wait import WebDriverWait

from ...common import ErroDeExecucao
from ...core import CrawJUD

# from ...shared import PropertiesCrawJUD


class capa(CrawJUD):  # noqa: N801
    """Manages 'capa' related tasks within the application.

    Inherits from CrawJUD to utilize core functionalities for processing 'capa' operations.

    Attributes:
        start_time (float): Timestamp marking the start of execution.
        max_rows (int): Total number of rows to process.
        row (int): Current row being processed.
        bot_data (dict): Data associated with the current bot operation.
        isStoped (bool): Flag indicating if the execution should stop.

    """

    def __init__(self, *args, **kwrgs) -> None:
        """Initialize the capa instance.

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
        """Execute the main process for 'capa' operations.

        Iterates through each row of data, managing the execution flow,
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
                        self.DriverLaunch(message="Webdriver encerrado inesperadamente, reinicializando...")

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
        """Queue the tasks for processing.

        Executes the sequence of actions required to process a 'capa', including
        searching for the bot and adding processes.

        Raises:
            ErroDeExecucao: If an error occurs during the queuing process.

        """
        try:
            self.search_bot()
            self.append_success(self.get_process_informations())

        except Exception as e:
            raise ErroDeExecucao(e=e) from e

    def get_process_informations(self) -> list:  # noqa: C901
        """Retrieve process information.

        Returns:
            list: A list containing process information.

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
                EC.presence_of_element_located((By.CSS_SELECTOR, self.elements.acao))
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
                EC.presence_of_element_located((By.CSS_SELECTOR, self.elements.vara_processual))
            ).text.split(" ")[0]
            foro: WebElement = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.elements.vara_processual))
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
                    .until(EC.presence_of_element_located((By.ID, self.elements.id_valor)))
                    .text
                )

            def converte_valor_causa(valor_causa) -> str:
                if "R$" in valor_causa:
                    valor_causa = float(
                        valor_causa.replace("$", "")
                        .replace("R", "")
                        .replace(" ", "")
                        .replace(".", "")
                        .replace(",", ".")
                    )
                    return "{:.2f}".format(valor_causa).replace(".", ",")

                if "R$" not in valor_causa:
                    valor_causa = float(valor_causa.replace("$", "").replace("R", "").replace(" ", "").replace(",", ""))
                    return "{:.2f}".format(valor_causa).replace(".", ",")

            valorDaCausa = valor  # noqa: N806
            if valor != "":
                valorDaCausa = converte_valor_causa(valor)  # noqa: N806

            sleep(0.5)
            distnotformated: WebElement = (
                self.wait.until(EC.presence_of_element_located((By.ID, self.elements.data_processual)))
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
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.elements.sumary_header_1))
            )

            sumary_2_esaj = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.elements.sumary_header_2))
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

                pass

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
