"""Robô de automação elaw andamentos."""

from __future__ import annotations

from time import sleep
from typing import NoReturn

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from app.common.exceptions.bot import ExecutionError
from app.controllers.elaw import ElawBot
from app.custom.task import ContextTask
from app.decorators import shared_task
from app.decorators.bot import wrap_cls
from app.resources.elements import elaw as el


def raise_error(message: str) -> NoReturn:
    """Empty.

    Raises:
        ExecutionError: ExecutionError

    """
    raise ExecutionError(message=message)


@shared_task(name="elaw.andamentos", bind=True, context=ContextTask)
@wrap_cls
class Andamentos(ElawBot):
    """The Andamentos class manages the andamento tracking bot."""

    def execution(self) -> None:
        """Execute the main processing loop for andamentos.

        Iterates over each entry in the data frame and processes it.
        Handles session expiration and error logger.

        """
        frame = self.frame
        self.total_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value

            self.queue()

        self.finalize_execution()

    def queue(self) -> None:
        """Handle the andamento queue processing.

        Attempts to perform the andamento operations and handles cases where the process is not found.
        """
        try:
            search = self.search()
            if not search:
                return

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

        except (ExecutionError, Exception) as e:
            self.append_error(exc=e)

    def info_data(self) -> None:
        """Inform the date of the andamento.

        This method fills in the date field in the andamento form.

        Raises:
            ExecutionError: If an error occurs while informing the date.

        """
        try:
            message = "Informando data"
            type_log = "log"
            self.print_msg(message=message, type_log=type_log, row=self.row)
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
            campo_data.send_keys(self.bot_data.get("DATA"))
            campo_data.send_keys(Keys.TAB)

            self.driver.sleep_load('div[id="j_id_34"]')

        except ExecutionError as e:
            raise ExecutionError(exc=e) from e

    def info_ocorrencia(self) -> None:
        """Inform the occurrence details of the andamento.

        This method fills in the occurrence details in the andamento form.

        Raises:
            ExecutionError: If an error occurs while informing the occurrence.

        """
        try:
            message = "Informando ocorrência"
            type_log = "log"
            self.print_msg(message=message, type_log=type_log, row=self.row)

            ocorrencia = self.driver.find_element(
                By.CSS_SELECTOR,
                el.inpt_ocorrencia,
            )
            text_andamento = (
                str(self.bot_data.get("OCORRENCIA"))
                .replace("\t", "")
                .replace("\n", "")
            )

            ocorrencia.send_keys(text_andamento)

        except ExecutionError as e:
            raise ExecutionError(exc=e) from e

    def info_observacao(self) -> None:
        """Inform the observation details of the andamento.

        This method fills in the observation details in the andamento form.

        Raises:
            ExecutionError: If an error occurs while informing the observation.

        """
        try:
            message = "Informando observação"
            type_log = "log"
            self.print_msg(message=message, type_log=type_log, row=self.row)

            observacao = self.driver.find_element(
                By.CSS_SELECTOR,
                el.inpt_obs,
            )
            text_andamento = (
                str(self.bot_data.get("OBSERVACAO"))
                .replace("\t", "")
                .replace("\n", "")
            )

            observacao.send_keys(text_andamento)

        except ExecutionError as e:
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
            message = "Salvando andamento..."
            type_log = "log"
            self.print_msg(message=message, type_log=type_log, row=self.row)
            sleep(1)
            self.link = self.driver.current_url
            save_button = self.driver.find_element(
                By.ID,
                el.botao_salvar_andamento,
            )
            save_button.click()

        except ExecutionError as e:
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
