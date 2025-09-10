"""Module for managing provision entries and updates in the ELAW system.

This module handles provision creation, updates and management within the ELAW system.
It automates the process of recording provisions and their associated documentation.

Classes:
    Provisao: Manages provision entries by extending the CrawJUD base class

Attributes:
    type_doc (dict): Maps document lengths to document types (CPF/CNPJ)

"""

from __future__ import annotations

from contextlib import suppress
from datetime import datetime
from time import sleep
from typing import TYPE_CHECKING

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.elaw import ElawBot
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task
from crawjud.decorators.bot import wrap_cls
from crawjud.resources.elements import elaw as el

if TYPE_CHECKING:
    from crawjud.utils.webdriver.web_element import WebElementBot as WebElement

type_doc = {11: "cpf", 14: "cnpj"}


@shared_task(name="elaw.provisao", bind=True, context=ContextTask)
@wrap_cls
class Provisao(ElawBot):
    """The Provisao class extends CrawJUD to manage provisions within the application.

    Attributes:
        attribute_name (type): Description of the attribute.


    """

    def execution(self) -> None:
        """Execute the main processing loop for provisions."""
        frame = self.frame
        self.total_rows = len(frame)
        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value

            self.queue()

        self.finalize_execution()

    def queue(self) -> None:
        try:
            search = self.search()
            if not search:
                message = "Processo não encontrado!"
                type_log = "error"
                self.print_msg(
                    message=message,
                    type_log=type_log,
                    row=self.row,
                )
                return

            type_log = "log"
            message = "Processo encontrado! Informando valores..."
            self.print_msg(message=message, type_log=type_log, row=self.row)

            calls = self.setup_calls()

            for call in calls:
                call()

            self.save_changes()

        except Exception as e:
            self.append_error(exc=e)

    def verifica_classe_risco(self) -> None:
        label_classificacao_risco = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.CSS_LABEL_TIPO_RISCO,
            )),
        )

        if label_classificacao_risco.text == "Risco Quebrado":
            element_select: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, el.CSS_SELETOR_TIPO_RISCO)),
            )

            element_select.select2("Risco")

    def setup_calls(self) -> list:
        calls = []

        verifica_valores = self.get_valores_proc()

        provisao = (
            str(self.bot_data.get("PROVISAO")).replace("possivel", "possível").replace("provavel", "provável").lower()
        )

        is_valores_and_possivel = all([verifica_valores == "Contém valores", provisao == "possível"])

        if is_valores_and_possivel:
            message = "Aviso: Já existe uma provisão possível cadastrada."
            type_log = "info"
            self.print_msg(message=message, type_log=type_log, row=self.row)

        edit_button = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_btn_edit,
            )),
        )
        edit_button.click()

        if verifica_valores == "Nenhum registro encontrado!":
            calls.extend([
                self.adiciona_nova_provisao,
                self.edita_provisao,
                self.verifica_classe_risco,
                self.atualiza_valores,
                self.informar_datas,
            ])

        elif verifica_valores == "Contém valores" or verifica_valores == "-":
            calls.extend([self.edita_provisao, self.verifica_classe_risco, self.atualiza_valores])

            if provisao == "provável" or provisao == "possível":
                calls.append(self.informar_datas)

        calls.extend([self.atualiza_risco, self.informar_motivo])

        return calls

    def get_valores_proc(self) -> str:
        verifica_valores = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.ver_valores,
            )),
        )
        verifica_valores.click()

        check_exists_provisao = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.table_valores_css,
            )),
        )
        check_exists_provisao = check_exists_provisao.find_elements(
            By.TAG_NAME,
            "tr",
        )

        for item in check_exists_provisao:
            item = item
            _item_text = str(item.text).split("\n")
            valueprovisao = item.find_elements(By.TAG_NAME, "td")[0].text
            with suppress(NoSuchElementException):
                valueprovisao = item.find_element(
                    By.CSS_SELECTOR,
                    el.value_provcss,
                ).text

            if "-" in valueprovisao or valueprovisao == "Nenhum registro encontrado!":
                return valueprovisao

        return "Contém valores"

    def adiciona_nova_provisao(self) -> None:
        try:
            div_tipo_obj = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.div_tipo_obj_css,
                )),
            )

            div_tipo_obj.click()

            item_obj_div = (
                self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        el.itens_obj_div_css,
                    )),
                )
                .find_element(By.TAG_NAME, "ul")
                .find_elements(By.TAG_NAME, "li")[0]
                .find_element(By.CSS_SELECTOR, el.checkbox)
            )

            item_obj_div.click()

            add_objeto = self.driver.find_element(
                By.CSS_SELECTOR,
                el.botao_adicionar,
            )
            add_objeto.click()

            self.sleep_load('div[id="j_id_8c"]')

        except ExecutionError as e:
            raise ExecutionError(
                message="Não foi possivel atualizar provisão",
                e=e,
            ) from e

    def edita_provisao(self) -> None:
        editar_pedido = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.botao_editar,
            )),
        )
        editar_pedido.click()

    def atualiza_valores(self) -> None:
        self.sleep_load('div[id="j_id_2z"]')
        message = "Informando valores"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        for row_valor in self.__tabela_valores():
            campo_valor_dml = row_valor.find_elements(By.TAG_NAME, "td")[9].find_element(
                By.CSS_SELECTOR,
                'input[id*="_input"]',
            )

            valor_informar = self.bot_data.get("VALOR_ATUALIZACAO")

            campo_valor_dml.send_keys(Keys.CONTROL + "a")
            campo_valor_dml.send_keys(Keys.BACKSPACE)
            self.sleep_load('div[id="j_id_2z"]')

            if isinstance(valor_informar, int):
                valor_informar = str(valor_informar) + ",00"

            elif isinstance(valor_informar, float):
                valor_informar = f"{valor_informar:.2f}".replace(".", ",")

            campo_valor_dml.send_keys(valor_informar)

            id_campo_valor_dml = campo_valor_dml.get_attribute("id")
            self.driver.execute_script(
                f"document.getElementById('{id_campo_valor_dml}').blur()",
            )
            self.sleep_load('div[id="j_id_2z"]')

    def atualiza_risco(self) -> None:
        self.driver.execute_script(
            'document.getElementById("j_id_2z:j_id_32_2e:processoAmountObjetoDt").style.zoom = "0.5" ',
        )
        message = "Alterando risco"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        for row_risco in self.__tabela_valores():
            selector_filter_risco = (
                row_risco.find_elements(By.TAG_NAME, "td")[10]
                .find_element(By.TAG_NAME, "div")
                .find_element(By.TAG_NAME, "select")
            )

            id_selector = selector_filter_risco.get_attribute("id")

            css_element = el.CSS_SELETOR_FILTRA_RISCO.format(id_selector=id_selector)

            element_select: WebElement = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, css_element)))

            provisao_from_xlsx = (
                str(self.bot_data.get("PROVISAO"))
                .lower()
                .replace("possivel", "possível")
                .replace("provavel", "provável")
            )

            element_select.select2(provisao_from_xlsx)

            self.sleep_load('div[id="j_id_3c"]')

    def informar_datas(self) -> None:
        message = "Alterando datas de correção base e juros"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        data_base_correcao = self.bot_data.get("DATA_BASE_CORRECAO")
        data_base_juros = self.bot_data.get("DATA_BASE_JUROS")
        if data_base_correcao is not None:
            if isinstance(data_base_correcao, datetime):
                data_base_correcao = data_base_correcao.strftime("%d/%m/%Y")

            self.set_data_correcao(data_base_correcao)

        if data_base_juros is not None:
            if isinstance(data_base_juros, datetime):
                data_base_juros = data_base_juros.strftime("%d/%m/%Y")

            self.set_data_juros(data_base_juros)

    def informar_motivo(self) -> None:
        """Inform the justification for the provision.

        Raises:
            None

        """
        try_salvar = self.driver.find_element(
            By.CSS_SELECTOR,
            el.CSS_BTN_SALVAR,
        )

        sleep(1)
        try_salvar.click()

        self.sleep_load('div[id="j_id_2z"]')

        message = "Informando justificativa"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)
        informar_motivo = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.CSS_TEXTAREA_MOTIVO,
            )),
        )
        informar_motivo.send_keys(
            self.bot_data.get("OBSERVACAO", "Atualização de provisão"),
        )
        id_informar_motivo = informar_motivo.get_attribute("id")
        self.driver.execute_script(
            f"document.getElementById('{id_informar_motivo}').blur()",
        )

    def save_changes(self) -> None:
        """Save all changes made during the provision process.

        Raises:
            ExecutionError: If unable to save the provision.

        """
        self.sleep_load('div[id="j_id_2z"]')
        salvar = self.driver.find_element(
            By.CSS_SELECTOR,
            el.CSS_BTN_SALVAR,
        )
        salvar.click()

        check_provisao_atualizada = None
        with suppress(TimeoutException):
            check_provisao_atualizada = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "#valoresGeralPanel_header > span",
                )),
            )

        if not check_provisao_atualizada:
            raise ExecutionError(message="Não foi possivel atualizar provisão")

        message = "Provisão atualizada com sucesso!"
        self.print_comprovante(message=message)

    def set_data_correcao(self, data_base_correcao: str) -> None:
        data_correcao = self.driver.find_element(
            By.CSS_SELECTOR,
            el.CSS_DATA_CORRECAO,
        )
        css_daata_correcao = data_correcao.get_attribute("id")
        data_correcao.clear()
        data_correcao.send_keys(data_base_correcao)

        self.driver.execute_script(
            f"document.getElementById('{css_daata_correcao}').blur()",
        )
        self.sleep_load('div[id="j_id_2z"]')

    def set_data_juros(self, data_base_juros: str) -> None:
        data_juros = self.driver.find_element(
            By.CSS_SELECTOR,
            el.CSS_DATA_JUROS,
        )
        css_data = data_juros.get_attribute("id")
        data_juros.clear()
        data_juros.send_keys(data_base_juros)
        self.driver.execute_script(
            f"document.getElementById('{css_data}').blur()",
        )
        self.sleep_load('div[id="j_id_2z"]')

    def __tabela_valores(self) -> list[WebElement]:
        return self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.CSS_TABELA_VALORES,
            )),
        ).find_elements(
            By.XPATH,
            el.XPATH_ROWS_VALORES_TABELA,
        )
