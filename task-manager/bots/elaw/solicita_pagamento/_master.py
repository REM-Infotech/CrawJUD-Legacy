"""Module for managing payment solution processes within the ELAW system.

This module provides functionality to handle payment management and solution creation within
the ELAW system. It enables automated payment processing, validations, and record-keeping.

Classes:
    SolPags: Handles payment solutions by extending the CrawJUD base class

Attributes:
    type_doc (dict): Maps document lengths to document types (CPF/CNPJ)

"""

from contextlib import suppress
from time import sleep
from typing import TYPE_CHECKING

from app.bots.elaw.solicita_pagamento._condenacao import ElawCondenacao
from app.bots.elaw.solicita_pagamento._custas import ElawCustas
from app.common import _raise_execution_error
from app.common.exceptions.bot import ExecutionError
from app.interfaces.types.bots import DataSucesso
from resources.elements import elaw as el
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

if TYPE_CHECKING:
    from collections.abc import Callable

    from app.utils.webdriver import WebElementBot as WebElement
type_doc = {11: "cpf", 14: "cnpj"}


class ElawPagamentos(ElawCustas, ElawCondenacao):
    def novo_pagamento(self) -> None:
        """Create a new payment entry.

        Raises:
            ExecutionError: If an error occurs during payment creation.

        """
        try:
            tab_pagamentos: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.valor_pagamento,
                )),
            )
            tab_pagamentos.click()

            novo_pgto: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.botao_novo_pagamento,
                )),
            )
            novo_pgto.click()

        except Exception as e:
            raise ExecutionError(e=e) from e

    def seleciona_tipo_pagamento(self, namedef: str) -> None:
        message = "Informando tipo de pagamento"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        type_itens: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_typeitens,
            )),
        )
        type_itens.click()

        sleep(0.5)

        list_itens: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.listitens_css,
            )),
        )
        list_itens = list_itens.find_elements(By.TAG_NAME, "li")

        for item in list_itens:
            item: WebElement = item

            normalizado_text = self.format_string(item.text)

            if normalizado_text.lower() == namedef.lower():
                item.click()
                return

            if "_" in normalizado_text:
                normalizado_text = normalizado_text.split("_")
                for norm in normalizado_text:
                    if norm.lower() == namedef.lower():
                        item.click()
                        return

        _raise_execution_error(message="Tipo de Pagamento não encontrado")

    def save_changes(self) -> None:
        try:
            message = "Salvando alterações"
            type_log = "log"
            self.print_msg(message=message, type_log=type_log, row=self.row)
            save: WebElement = self.wait.until(
                ec.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    el.botao_salvar_pagamento,
                )),
            )
            save.click()

        except Exception as e:
            raise ExecutionError(e=e) from e

    def confirm_save(self) -> None:
        main_frame = self.driver.current_window_handle
        now = self.current_time
        data = None

        message = "Pagamento não encontrado!"

        tab_pagamentos: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.valor_pagamento,
            )),
        )
        tab_pagamentos.click()

        check_solicitacoes: list[WebElement] = (
            self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.valor_resultado,
                )),
            )
            .find_element(By.TAG_NAME, "table")
            .find_element(By.TAG_NAME, "tbody")
            .find_elements(By.TAG_NAME, "tr")
        )

        numero_processo = self.bot_data.get("NUMERO_PROCESSO")

        name_comprovante1 = (
            f"COMPROVANTE 1 {numero_processo} - {self.pid} - {now}.png"
        )
        path_comprovante1 = self.output_dir_path.joinpath(name_comprovante1)

        name_comprovante2 = (
            f"COMPROVANTE 2 {numero_processo} - {self.pid} - {now}.png"
        )
        path_comprovante2 = self.output_dir_path.joinpath(name_comprovante2)

        codigo_barras_planilha = str(
            self.bot_data.get("COD_BARRAS").replace(".", "").replace(" ", ""),
        )
        tipo_condenacao_xls = str(self.bot_data.get("TIPO_CONDENACAO", ""))
        tipo_custa_xls = str(self.bot_data.get("TIPO_GUIA", ""))
        namedef = self.format_string(
            self.bot_data.get("TIPO_PAGAMENTO"),
        ).lower()

        for pos, item in enumerate(check_solicitacoes):
            if item.text == "Nenhum registro encontrado!":
                _raise_execution_error(message=message)

            id_task = item.find_elements(By.TAG_NAME, "td")[2].text

            open_details = item.find_element(By.CSS_SELECTOR, el.botao_ver)
            open_details.click()

            frame_pgto, close_context = self.__get_frame_pgto(pos)

            tipo_custa, codigo_de_barras, tipo_condenacao = (
                self.__informacoes_para_comparar()
            )

            check_codigo_barras = codigo_de_barras == codigo_barras_planilha

            if namedef == "condenacao":
                match_condenacao = (
                    tipo_condenacao_xls.lower() == tipo_condenacao.lower()
                )
                matchs = all([match_condenacao, check_codigo_barras])

            elif namedef == "custas":
                match_custa = tipo_custa_xls.lower() == tipo_custa.lower()
                matchs = all([match_custa, check_codigo_barras])

            if matchs:
                url_page = frame_pgto.get_attribute("src")
                self.screenshot_iframe(url_page, path_comprovante1)
                close_context(main_frame)

                with path_comprovante2.open("wb") as fp:
                    fp.write(item.screenshot_as_png)

                message = "Pagamento realizado com sucesso!"

                data = DataSucesso(
                    NUMERO_PROCESSO=numero_processo,
                    MENSAGEM=message,
                    NOME_COMPROVANTE=name_comprovante1,
                    NOME_COMPROVANTE_2=name_comprovante2,
                )

                data["ID_CONTROLE_ELAW"] = id_task
                break

            close_context(main_frame)

        if not data:
            _raise_execution_error(message=message)

        self.append_success(data=data)
        self.print_msg(message=message, type_log="success", row=self.row)

    def __get_frame_pgto(
        self,
        pos: int,
    ) -> tuple[WebElement, Callable[[str], None]]:
        close_context = self.wait.until(
            ec.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    f'div[id="tabViewProcesso:pvp-dtProcessoValorResults:{pos}:pvp-pgBotoesValoresPagamentoBtnVer_dlg"]',
                ),
            ),
        ).find_element(By.TAG_NAME, "a")

        frame_pgto = WebDriverWait(self.driver, 5).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, el.valor)),
        )
        self.driver.switch_to.frame(frame_pgto)

        def context_switch(main_frame: str) -> None:
            close_context.click()
            self.driver.switch_to.frame(main_frame)

        return frame_pgto, context_switch

    def __informacoes_para_comparar(self) -> tuple[str, str, str]:
        tipo_custa = ""
        codigo_de_barras = ""
        tipo_condenacao = ""

        with suppress(TimeoutException):
            tipo_custa = str(
                self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        el.visualizar_tipo_custas,
                    )),
                )
                .text.split(":")[-1]
                .replace("\n", ""),
            )

        with suppress(TimeoutException):
            codigo_de_barras = str(
                self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        el.visualizar_cod_barras,
                    )),
                )
                .text.split(":")[-1]
                .replace("\n", ""),
            )

        with suppress(TimeoutException):
            tipo_condenacao = (
                self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        el.visualizar_tipo_condenacao,
                    )),
                )
                .text.split(":")[-1]
                .replace("\n", "")
            )

        return tipo_custa, codigo_de_barras, tipo_condenacao
