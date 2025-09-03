"""Module for managing deadline tracking and recording in the ELAW system.

This module provides functionality for creating, updating and tracking deadlines within
the ELAW system. It automates the process of recording and monitoring time-sensitive tasks.

Classes:
    Prazos: Manages deadline entries by extending the CrawJUD base class
"""

from __future__ import annotations

from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from crawjud.common import _raise_execution_error
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.elaw import ElawBot
from crawjud.resources.elements import elaw as el

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement


class Prazos(ElawBot):
    """The Prazos class extends CrawJUD to handle deadline-related tasks within the application.

    Attributes:
        attribute_name (type): Description of the attribute.


    """

    def execution(self) -> None:
        """Execute the main processing loop for deadlines."""
        frame = self.frame
        self.total_rows = len(frame)

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

                self.bot_data.update({"MOTIVO_ERRO": message_error})
                self.append_error(self.bot_data)

                self.message_error = None

        self.finalize_execution()

    def queue(self) -> None:
        """Handle the deadline queue processing.

        Raises:
            ExecutionError: If an error occurs during execution.

        """
        try:
            search = self.search_bot()
            if not search:
                self.message = "Buscando Processo"
                _raise_execution_error(message="Não Encontrado!")

            comprovante = ""
            self.data_Concat = f"{self.bot_data['DATA_AUDIENCIA']} {self.bot_data['HORA_AUDIENCIA']}"
            self.message = "Processo Encontrado!"
            self.type_log = "log"
            self.prt()

            self.tabela_pautas()
            chk_lancamento = self.checar_lancamento()

            if chk_lancamento:
                self.message = "Já existe lançamento para esta pauta"
                self.type_log = "info"
                chk_lancamento.update({
                    "MENSAGEM_COMCLUSAO": "REGISTROS ANTERIORES EXISTENTES!",
                })

                comprovante = chk_lancamento

            if not comprovante:
                self.nova_pauta()
                self.salvar_prazo()
                comprovante = self.checar_lancamento()
                if not comprovante:
                    _raise_execution_error(
                        message="Não foi possível comprovar lançamento, verificar manualmente",
                    )

                self.message = "Pauta lançada!"

            self.append_success([comprovante], self.message)

        except ExecutionError as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(exc=e) from e

    def tabela_pautas(self) -> None:
        """Verify if there are existing schedules for the specified day.

        Raises:
            ExecutionError: If an error occurs during the verification process.

        """
        try:
            switch_pautaandamento = self.driver.find_element(
                By.CSS_SELECTOR,
                el.switch_pautaandamento,
            )

            switch_pautaandamento.click()

            self.message = (
                f"Verificando se existem pautas para o dia {self.data_Concat}"
            )
            self.type_log = "log"
            self.prt()

        except ExecutionError as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(exc=e) from e

    def nova_pauta(self) -> None:
        """Launch a new audience schedule.

        Raises:
            ExecutionError: If unable to launch a new audience.

        """
        try:
            self.message = "Lançando nova audiência"
            self.type_log = "log"
            self.prt()

            btn_novaaudiencia = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.btn_novaaudiencia,
                )),
            )

            btn_novaaudiencia.click()

            # Info tipo Audiencia
            self.message = "Informando tipo de audiência"
            self.type_log = "log"
            self.prt()

            selectortipoaudiencia = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.selectortipoaudiencia,
                )),
            )

            items = selectortipoaudiencia.find_elements(By.TAG_NAME, "option")
            opt_itens: dict[str, str] = {}
            for item in items:
                value_item = item.get_attribute("value")
                text_item = self.driver.execute_script(
                    f"return $(\"option[value='{value_item}']\").text();",
                )

                opt_itens.update({text_item.upper(): value_item})

            value_opt = opt_itens.get(self.bot_data["TIPO_AUDIENCIA"].upper())
            if value_opt:
                command = (
                    f"$('{el.selectortipoaudiencia}').val(['{value_opt}']);"
                )
                self.driver.execute_script(command)

                command2 = (
                    f"$('{el.selectortipoaudiencia}').trigger('change');"
                )
                self.driver.execute_script(command2)

            # Info Data Audiencia
            self.message = "Informando data da Audiência"
            self.type_log = "log"
            self.prt()

            data_audiencia = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.data_audiencia,
                )),
            )

            data_audiencia.send_keys(self.data_Concat)

        except ExecutionError as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(exc=e) from e

    def salvar_prazo(self) -> None:
        """Save the newly created deadline.

        Raises:
            ExecutionError: If unable to save the deadline.

        """
        try:
            self.message = "Salvando..."
            self.type_log = "log"
            self.prt()

            btn_salvar = self.driver.find_element(
                By.CSS_SELECTOR,
                el.btn_salvar,
            )

            btn_salvar.click()

        except ExecutionError as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(exc=e) from e

    def checar_lancamento(self) -> dict[str, str] | None:
        """Check if the deadline has been successfully recorded.

        Returns:
            dict[str, str] | None: Details of the recorded deadline or None if not found.

        Raises:
            ExecutionError: If unable to verify the deadline record.

        """
        data = None
        try:
            tableprazos = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.tableprazos,
                )),
            )

            tableprazos: list[WebElement] = tableprazos.find_elements(
                By.TAG_NAME,
                "tr",
            )

            for item in tableprazos:
                if item.text == "Nenhum registro encontrado!":
                    return None

                data_prazo = str(item.find_elements(By.TAG_NAME, "td")[4].text)

                tipo = str(item.find_elements(By.TAG_NAME, "td")[5].text)

                chk_tipo = tipo.upper() == "AUDIÊNCIA"
                check_data_audiencia = data_prazo == self.data_Concat

                if chk_tipo and check_data_audiencia:
                    numero_processo_pid = (
                        f"{self.bot_data['NUMERO_PROCESSO']} - {self.pid}"
                    )

                    nome_comprovante = (
                        f"Comprovante - {numero_processo_pid}.png"
                    )
                    id_prazo = str(
                        item.find_elements(By.TAG_NAME, "td")[2].text,
                    )

                    item.screenshot(
                        str(
                            Path(self.output_dir_path).joinpath(
                                nome_comprovante,
                            ),
                        ),
                    )

                    data = {
                        "NUMERO_PROCESSO": str(
                            self.bot_data["NUMERO_PROCESSO"],
                        ),
                        "MENSAGEM_COMCLUSAO": "PRAZO LANÇADO",
                        "ID_PRAZO": id_prazo,
                        "NOME_COMPROVANTE": nome_comprovante,
                    }

        except ExecutionError as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35

            raise ExecutionError(exc=e) from e

        return data
