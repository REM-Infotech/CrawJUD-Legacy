"""Gerencie o protocolo de petições no sistema JusBr de forma automatizada.

Este módulo contém a classe Protocolo, responsável por executar o fluxo de
protocolo de petições judiciais utilizando automação com Selenium, incluindo
seleção de tipo de protocolo, upload de documentos e tratamento de erros.

"""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

import dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from tqdm import tqdm

from crawjud.common import _raise_execution_error
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.jusbr import JusBrBot
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task
from crawjud.decorators.bot import wrap_cls
from crawjud.resources import format_string
from crawjud.resources.elements import jusbr as el

if TYPE_CHECKING:
    from crawjud.utils.webdriver.web_element import WebElementBot

dotenv.load_dotenv()


@shared_task(name="jusbr.protocolo", bind=True, base=ContextTask)
@wrap_cls
class Protocolo(JusBrBot):
    """Gerencia o protocolo de petições no sistema JusBr."""

    def execution(self) -> None:
        """Executa o processamento principal de protocolo para cada linha do DataFrame."""
        frame = self.frame
        self._total_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth()

            try:
                self.queue()

            except (ExecutionError, Exception) as e:
                message_error = str(e)

                self.print_msg(message=f"{message_error}.", type_log="error")

                self.bot_data.update({"MOTIVO_ERRO": message_error})
                self.append_error(self.bot_data)

                self.message_error = None

        self.finalize_execution()

    def queue(self) -> None:
        """Realiza a fila de protocolo para o processo informado no DataFrame."""
        bot_data = self.bot_data
        search = self.search(method="peticionamento")

        if not search:
            self.print_msg(
                message="Processo não encontrado!",
                type_log="error",
                row=self.row,
            )
            return

        self.__seleciona_tipo_protocolo()
        self.__peticao_principal()

        if "ANEXOS" in bot_data and bot_data["ANEXOS"].strip():
            self.__anexos_protocolo()

        _processo = bot_data["NUMERO_PROCESSO"]
        tqdm.write("ok")

    def __seleciona_tipo_protocolo(self) -> None:
        """Seleciona o tipo de protocolo conforme informado nos dados do DataFrame."""
        wait = self.wait
        bot_data = self.bot_data
        seletor_tipo_peticionamento = wait.until(
            ec.presence_of_element_located((
                By.CLASS_NAME,
                el.campo_tipo_protocolo,
            )),
        )

        seletor_tipo_peticionamento.click()

        items_tipo_processo = wait.until(
            ec.presence_of_all_elements_located((
                By.XPATH,
                el.tipos_protocolos,
            )),
        )

        filter_tipo = list(
            filter(
                lambda x: bot_data["TIPO_PROTOCOLO"].lower() in x.text.lower(),
                items_tipo_processo,
            ),
        )

        if len(filter_tipo) == 0:
            _raise_execution_error(message="Tipo de protocolo não encontrado!")

        filter_tipo[-1].click()

    def __peticao_principal(self) -> None:
        """Realiza o upload da petição principal e selecione o tipo de documento."""
        wait = self.wait
        bot_data = self.bot_data

        path_peticao = str(
            self.output_dir_path.joinpath(
                format_string(bot_data["PETICAO_PRINCIPAL"]),
            ),
        )

        input_peticao_principal: WebElementBot = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.campo_arquivo_principal,
            )),
        )

        input_peticao_principal.send_keys(path_peticao)

        campo_tipo_doc = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.campo_tipo_documento,
            )),
        )

        campo_tipo_doc.click()

        tipos_docs = wait.until(
            ec.presence_of_all_elements_located((
                By.XPATH,
                el.options_tipo_documento,
            )),
        )

        filter_tipo = list(
            filter(
                lambda x: bot_data["TIPO_PETIÇÃO"].lower() in x.text.lower(),
                tipos_docs,
            ),
        )

        if len(filter_tipo) == 0:
            _raise_execution_error(message="Tipo de protocolo não encontrado!")

        filter_tipo[-1].click()

    def __anexos_protocolo(self) -> None:
        """Empty."""
        driver = self.driver
        bot_data = self.bot_data
        row_anexo = 2
        element_select_anexos = f'mat-select[id="mat-select-{row_anexo}"]'

        anexos = (
            bot_data["ANEXOS"].split(",")
            if "," in bot_data["ANEXOS"]
            else [bot_data["ANEXOS"]]
        )

        for _item in anexos:
            driver.find_element(By.CSS_SELECTOR, element_select_anexos).click()

            row_anexo += 2
