"""Module for tracking and recording process progress in the ELAW system.

This module handles the creation and management of process progress records within the ELAW
system. It automates the recording of progress updates and related documentation.

Classes:
    Andamentos: Manages process progress by extending the CrawJUD base class
"""

from __future__ import annotations

from contextlib import suppress
from time import sleep

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.elaw import ElawBot
from crawjud.resources.elements import elaw as el


class Andamentos(ElawBot):
    """The Andamentos class manages the andamento tracking bot."""

    def execution(self) -> None:
        """Execute the main processing loop for andamentos.

        Iterates over each entry in the data frame and processes it.
        Handles session expiration and error logger.

        """
        frame = self.dataFrame()
        self.max_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth_bot()

            try:
                self.queue()

            except ExecutionError as e:
                windows = self.driver.window_handles

                if len(windows) == 0:
                    with suppress(Exception):
                        self.driver_launch(
                            message="Webdriver encerrado inesperadamente, reinicializando...",
                        )

                    self.auth_bot()

                message_error = str(e)

                self.print_msg(message=f"{message_error}.", type_log="error")

                self.bot_data.update({"MOTIVO_ERRO": self.message_error})
                self.append_error(self.bot_data)

                self.message_error = None

        self.finalize_execution()

    def queue(self) -> None:
        """Handle the andamento queue processing.

        Attempts to perform the andamento operations and handles cases where the process is not found.

        Raises:
            ExecutionError: If an error occurs during queue processing.

        """
        try:
            search = self.search_bot()
            if search is True:
                btn_newmove = el.botao_andamento
                new_move = self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        btn_newmove,
                    )),
                )
                new_move.click()

                self.info_data()
                self.info_ocorrencia()
                self.info_observacao()

                if self.bot_data.get("ANEXOS", None):
                    self.add_anexo()

                self.save_andamento()

            elif search is not True:
                self.message = "Processo não encontrado!"
                self.type_log = "error"
                self.prt()
                self.append_error([
                    self.bot_data.get("NUMERO_PROCESSO"),
                    self.message,
                ])

        except ExecutionError as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(exc=e) from e

    def info_data(self) -> None:
        """Inform the date of the andamento.

        This method fills in the date field in the andamento form.

        Raises:
            ExecutionError: If an error occurs while informing the date.

        """
        try:
            self.message = "Informando data"
            self.type_log = "log"
            self.prt()
            css_campo_data = el.input_data
            campo_data = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    css_campo_data,
                )),
            )
            campo_data.click()
            campo_data.send_keys(Keys.CONTROL, "a")
            sleep(0.5)
            campo_data.send_keys(Keys.BACKSPACE)
            self.interact.send_key(campo_data, self.bot_data.get("DATA"))
            campo_data.send_keys(Keys.TAB)

            self.interact.sleep_load('div[id="j_id_34"]')

        except ExecutionError as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(exc=e) from e

    def info_ocorrencia(self) -> None:
        """Inform the occurrence details of the andamento.

        This method fills in the occurrence details in the andamento form.

        Raises:
            ExecutionError: If an error occurs while informing the occurrence.

        """
        try:
            self.message = "Informando ocorrência"
            self.type_log = "log"
            self.prt()

            ocorrencia = self.driver.find_element(
                By.CSS_SELECTOR,
                el.inpt_ocorrencia,
            )
            text_andamento = (
                str(self.bot_data.get("OCORRENCIA"))
                .replace("\t", "")
                .replace("\n", "")
            )

            self.interact.send_key(ocorrencia, text_andamento)

        except ExecutionError as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(exc=e) from e

    def info_observacao(self) -> None:
        """Inform the observation details of the andamento.

        This method fills in the observation details in the andamento form.

        Raises:
            ExecutionError: If an error occurs while informing the observation.

        """
        try:
            self.message = "Informando observação"
            self.type_log = "log"
            self.prt()

            observacao = self.driver.find_element(
                By.CSS_SELECTOR,
                el.inpt_obs,
            )
            text_andamento = (
                str(self.bot_data.get("OBSERVACAO"))
                .replace("\t", "")
                .replace("\n", "")
            )

            self.interact.send_key(observacao, text_andamento)

        except ExecutionError as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(exc=e) from e

    def add_anexo(self) -> None:
        """Add attachments to the andamento.

        This method handles the addition of attachments to the andamento form.

        Raises:
            NotImplementedError: If the method is not yet implemented.

        """

    def save_andamento(self) -> None:
        """Save the andamento details.

        This method clicks the save button to persist the andamento data and verifies the save operation.

        Raises:
            ExecutionError: If the save operation fails or cannot be validated.

        """
        try:
            self.message = "Salvando andamento..."
            self.type_log = "log"
            self.prt()
            sleep(1)
            self.link = self.driver.current_url
            save_button = self.driver.find_element(
                By.ID,
                el.botao_salvar_andamento,
            )
            save_button.click()

        except ExecutionError as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(
                message="Não foi possivel salvar andamento",
                e=e,
            ) from e

        check_save = WebDriverWait(self.driver, 10).until(
            ec.url_to_be("https://amazonas.elaw.com.br/processoView.elaw"),
        )
        if check_save:
            sleep(3)

            self.append_success(
                [self.numproc, "Andamento salvo com sucesso!", ""],
                "Andamento salvo com sucesso!",
            )
