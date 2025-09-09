"""Module for managing payment solution processes within the ELAW system.

This module provides functionality to handle payment management and solution creation within
the ELAW system. It enables automated payment processing, validations, and record-keeping.

Classes:
    SolPags: Handles payment solutions by extending the CrawJUD base class

Attributes:
    type_doc (dict): Maps document lengths to document types (CPF/CNPJ)

"""

from __future__ import annotations

from contextlib import suppress
from datetime import datetime
from pathlib import Path
from time import sleep
from zoneinfo import ZoneInfo

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.common import _raise_execution_error
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.elaw import ElawBot
from crawjud.resources.elements import elaw as el

type_doc = {11: "cpf", 14: "cnpj"}


class SolPags(ElawBot):
    """The SolPags class extends CrawJUD to manage page solutions within the application.

    Attributes:
        attribute_name (type): Description of the attribute.


    """

    def execution(self) -> None:
        """Execute the main processing loop for page solutions."""
        frame = self.frame
        self.total_rows = len(frame)
        self.driver.maximize_window()
        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = self.elaw_formats(value)

            try:
                self.queue()

            except ExecutionError as e:
                windows = self.driver.window_handles

                if len(windows) == 0:
                    with suppress(Exception):
                        self.driver_launch(
                            message="Webdriver encerrado inesperadamente, reinicializando...",
                        )

                    self.auth()

                message_error = str(e)

                self.print_msg(message=f"{message_error}.", type_log="error")

                self.bot_data.update({"MOTIVO_ERRO": message_error})
                self.append_error(self.bot_data)

                self.message_error = None

        self.finalize_execution()

    def queue(self) -> None:
        """Handle the solution queue processing.

        Raises:
            ExecutionError: If an error occurs during execution.

        """
        try:
            search = self.search()

            if search is True:
                namedef = self.format_string(
                    self.bot_data.get("TIPO_PAGAMENTO"),
                )
                self.new_payment()
                self.set_pgto(namedef)
                pgto = getattr(self, namedef.lower())
                pgto()

                self.save_changes()
                self.append_success(self.confirm_save())

            elif search is not True:
                _raise_execution_error(message="Processo não encontrado!")

        except ExecutionError as e:
            raise ExecutionError(exc=e) from e

    def new_payment(self) -> None:
        """Create a new payment entry.

        Raises:
            ExecutionError: If an error occurs during payment creation.

        """
        try:
            tab_pagamentos = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.valor_pagamento,
                )),
            )
            tab_pagamentos.click()

            novo_pgto = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.botao_novo_pagamento,
                )),
            )
            novo_pgto.click()

        except ExecutionError as e:
            raise ExecutionError(exc=e) from e

    def set_pgto(self, namedef: str) -> None:
        """Set the payment type.

        Args:
            namedef (str): The name definition for the payment type.

        Raises:
            ExecutionError: If the payment type is not found.

        """
        try:
            self.message = "Informando tipo de pagamento"
            self.type_log = "log"
            self.prt()

            type_itens = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.css_typeitens,
                )),
            )
            type_itens.click()

            sleep(0.5)

            list_itens = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.listitens_css,
                )),
            )
            list_itens = list_itens.find_elements(By.TAG_NAME, "li")

            for item in list_itens:
                item = item

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

        except ExecutionError as e:
            raise ExecutionError(exc=e) from e

    def condenacao(self) -> None:
        """Refatore o processamento de condenação para reduzir a complexidade.

        Raises:
            ExecutionError: Se ocorrer erro durante o processamento da condenação.

        """
        try:
            self._informar_valor_guia()
            self._selecionar_tipo_documento()
            self._enviar_documentos_condenacao()
            self._informar_tipo_condenacao()
            self._informar_descricao_pagamento()
            self._informar_data_pagamento()
            self._informar_favorecido()
            self._informar_forma_pagamento()
            self._informar_centro_custas()
            self._informar_conta_debito()
        except ExecutionError as e:
            raise ExecutionError(exc=e) from e

    def _informar_valor_guia(self) -> None:
        """Informe o valor da guia no campo apropriado."""
        self.message = "Informando o valor da guia"
        self.type_log = "log"
        self.prt()
        text = self.bot_data.get("VALOR_GUIA")
        element = self.wait.until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                el.css_element,
            )),
        )
        sleep(0.5)
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.BACKSPACE)
        self.interact.send_key(element, text)
        self.driver.execute_script(
            f"document.querySelector('{el.css_element}').blur()",
        )
        self.sleep_load('div[id="j_id_2x"]')

    def _selecionar_tipo_documento(self) -> None:
        """Selecione o tipo de documento 'guia de pagamento'."""
        div_type_doc = self.wait.until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                el.type_doc_css,
            )),
        )
        div_type_doc.click()
        sleep(0.5)
        list_type_doc = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.list_type_doc_css,
            )),
        )
        list_type_doc = list_type_doc.find_elements(By.TAG_NAME, "li")
        for item in list_type_doc:
            if item.text.lower() == "guia de pagamento":
                item.click()
                break
        self.sleep_load('div[id="j_id_2x"]')

    def _enviar_documentos_condenacao(self) -> None:
        """Envie os documentos necessários para a condenação."""
        self.message = "Enviando guia"
        self.type_log = "log"
        self.prt()
        docs = [self.bot_data.get("DOC_GUIA")]
        calculo = self.bot_data.get("DOC_CALCULO", None)
        if calculo:
            calculos = [str(calculo)]
            if "," in str(calculo):
                calculos = str(calculo).split(",")
            docs.extend(calculos)
        for doc in docs:
            doc = self.format_string(doc.upper())
            insert_doc = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.editar_pagamento,
                )),
            )
            path_doc = str(Path(self.output_dir_path).joinpath(doc))
            insert_doc.send_keys(path_doc)
            self.interact.wait_fileupload()
            sleep(0.5)

    def _informar_tipo_condenacao(self) -> None:
        """Informe o tipo de condenação (sentença ou acórdão)."""
        self.message = "Informando tipo de condenação"
        self.type_log = "log"
        self.prt()
        div_condenacao_type = self.wait.until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                el.css_div_condenacao_type,
            )),
        )
        div_condenacao_type.click()
        tipo_condenacao = str(self.bot_data.get("TIPO_CONDENACAO"))
        if tipo_condenacao.lower() == "sentença":
            sleep(0.5)
            sentenca = self.driver.find_element(
                By.CSS_SELECTOR,
                el.valor_sentenca,
            )
            sentenca.click()
        elif tipo_condenacao.lower() == "acórdão":
            sleep(0.5)
            acordao = self.driver.find_element(
                By.CSS_SELECTOR,
                el.valor_acordao,
            )
            acordao.click()

    def _informar_descricao_pagamento(self) -> None:
        """Informe a descrição do pagamento."""
        self.message = "Informando descrição do pagamento"
        self.type_log = "log"
        self.prt()
        desc_pagamento = str(self.bot_data.get("DESC_PAGAMENTO"))
        desc_pgto = self.wait.until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                el.css_desc_pgto,
            )),
        )
        desc_pgto.click()
        desc_pagamento = desc_pagamento.replace("\n", "").replace("\t", "")
        desc_pgto.send_keys(desc_pagamento)
        sleep(0.5)
        self.driver.execute_script(
            f"document.querySelector('{el.css_desc_pgto}').blur()",
        )

    def _informar_data_pagamento(self) -> None:
        """Informe a data para pagamento."""
        self.message = "Informando data para pagamento"
        self.type_log = "log"
        self.prt()
        data_lancamento = self.wait.until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, el.css_data)),
        )
        data_lancamento.click()
        data_lancamento.send_keys(self.bot_data.get("DATA_LANCAMENTO"))
        data_lancamento.send_keys(Keys.TAB)
        self.driver.execute_script(
            f"document.querySelector('{el.css_data}').blur()",
        )
        self.sleep_load('div[id="j_id_2x"]')

    def _informar_favorecido(self) -> None:
        """Informe o favorecido do pagamento."""
        self.message = "Informando favorecido"
        self.type_log = "log"
        self.prt()
        input_favorecido = WebDriverWait(self.driver, 10).until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                el.css_inputfavorecido,
            )),
        )
        input_favorecido.click()
        input_favorecido.clear()
        sleep(2)
        input_favorecido.send_keys(
            self.bot_data.get("CNPJ_FAVORECIDO", "00.360.305/0001-04"),
        )
        result_favorecido = WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.resultado_favorecido,
            )),
        )
        result_favorecido.click()
        self.sleep_load('div[id="j_id_2x"]')

    def _informar_forma_pagamento(self) -> None:
        """Informe a forma de pagamento (boleto)."""
        self.message = "Informando forma de pagamento"
        self.type_log = "log"
        self.prt()
        label_forma_pgto = self.driver.find_element(
            By.CSS_SELECTOR,
            el.valor_processo,
        )
        label_forma_pgto.click()
        sleep(1)
        boleto = self.driver.find_element(By.CSS_SELECTOR, el.boleto)
        boleto.click()
        self.sleep_load('div[id="j_id_2x"]')
        campo_cod_barras = self.wait.until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                el.css_cod_bars,
            )),
        )
        campo_cod_barras.click()
        sleep(0.5)
        cod_barras = str(self.bot_data.get("COD_BARRAS"))
        campo_cod_barras.send_keys(
            cod_barras.replace("\t", "").replace("\n", ""),
        )
        self.driver.execute_script(
            f"document.querySelector('{el.css_cod_bars}').blur()",
        )
        self.sleep_load('div[id="j_id_2x"]')

    def _informar_centro_custas(self) -> None:
        """Informe o centro de custas."""
        self.message = "Informando centro de custas"
        self.type_log = "log"
        self.prt()
        centro_custas = self.wait.until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                el.css_centro_custas,
            )),
        )
        centro_custas.click()
        centro_custas.send_keys("A906030100")
        self.driver.execute_script(
            f"document.querySelector('{el.css_centro_custas}').blur()",
        )
        sleep(1)

    def _informar_conta_debito(self) -> None:
        """Informe a conta para débito."""
        self.message = "Informando conta para débito"
        self.type_log = "log"
        self.prt()
        div_conta_debito = self.wait.until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                el.css_div_conta_debito,
            )),
        )
        div_conta_debito.click()
        sleep(1)
        conta_debito = self.driver.find_element(
            By.CSS_SELECTOR,
            'li[data-label="AMAZONAS - PAGTO CONDENAÇÕES DE LITÍGIOS CÍVEIS CONTRAPARTIDA"]',
        )
        conta_debito.click()

    def custas(self) -> None:
        """Manage cost-related operations.

        Raises:
            ExecutionError: If an error occurs during cost management.

        """
        try:
            self.message = "Informando valor da guia"
            self.type_log = "log"
            self.prt()

            valor_doc = self.bot_data.get("VALOR_GUIA").replace(".", ",")

            element = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.valor_guia,
                )),
            )
            element.click()
            element.send_keys(Keys.CONTROL, "a")
            sleep(0.5)
            element.send_keys(Keys.BACK_SPACE)
            sleep(0.5)
            element.send_keys(valor_doc)

            self.driver.execute_script(
                f"document.querySelector('{el.valor_guia}').blur()",
            )

            sleep(0.5)

            list_tipo_doc = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.type_doc_css,
                )),
            )
            list_tipo_doc.click()
            sleep(1)

            set_gru = self.driver.find_element(By.CSS_SELECTOR, el.css_gru)
            set_gru.click()

            sleep(2)
            self.message = "Inserindo documento"
            self.type_log = "log"
            self.prt()

            docs = [self.bot_data.get("DOC_GUIA")]

            for doc in docs:
                doc = self.format_string(doc)
                insert_doc = self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        el.editar_pagamento,
                    )),
                )
                insert_doc.send_keys(f"{self.output_dir_path}/{doc}")

                wait_upload = (
                    WebDriverWait(self.driver, 20)
                    .until(
                        ec.presence_of_element_located((
                            By.CSS_SELECTOR,
                            el.editar_pagamentofile,
                        )),
                    )
                    .find_element(By.TAG_NAME, "table")
                    .find_element(By.TAG_NAME, "tbody")
                    .find_elements(By.TAG_NAME, "tr")
                )

                if len(wait_upload) == len(docs):
                    break

            solicitante = str(self.bot_data.get("SOLICITANTE")).lower()
            if (
                solicitante == "monitoria"
                or solicitante.lower() == "monitória"
            ):
                desc_pgto = self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        el.css_desc_pgto,
                    )),
                )
                desc_pgto.send_keys(self.bot_data.get("DESC_PAGAMENTO"))
                self.driver.execute_script(
                    f"document.querySelector('{el.css_desc_pgto}').blur()",
                )

            self.message = "Informando tipo de guia"
            self.type_log = "log"
            self.prt()

            div_tipo_custa = self.driver.find_element(
                By.CSS_SELECTOR,
                el.css_tipo_custa,
            )
            div_tipo_custa.click()
            sleep(1)

            tipo_guia = str(self.bot_data.get("TIPO_GUIA"))
            list_tipo_custa = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.css_listcusta,
                )),
            )
            list_tipo_custa = list_tipo_custa.find_elements(By.TAG_NAME, "li")
            for item in list_tipo_custa:
                item = item
                if tipo_guia.lower() == item.text.lower():
                    sleep(0.5)
                    item.click()
                    break

            sleep(1)
            self.message = "Informando data para pagamento"
            self.type_log = "log"
            self.prt()

            data_vencimento = self.driver.find_element(
                By.CSS_SELECTOR,
                el.css_data,
            )
            data_vencimento.click()
            data_vencimento.send_keys(self.bot_data.get("DATA_LANCAMENTO"))
            self.driver.execute_script(
                f"document.querySelector('{el.css_data}').blur()",
            )
            self.sleep_load('div[id="j_id_2x"]')

            label_forma_pgto = self.driver.find_element(
                By.CSS_SELECTOR,
                el.valor_processo,
            )
            label_forma_pgto.click()

            sleep(1)
            boleto = self.driver.find_element(By.CSS_SELECTOR, el.boleto)
            boleto.click()

            self.sleep_load('div[id="j_id_2x"]')

            campo_cod_barras = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.css_cod_bars,
                )),
            )
            campo_cod_barras.click()
            sleep(0.5)
            campo_cod_barras.send_keys(self.bot_data.get("COD_BARRAS"))
            self.driver.execute_script(
                f"document.querySelector('{el.css_cod_bars}').blur()",
            )

            self.message = "Informando favorecido"
            self.type_log = "log"
            self.prt()

            sleep(2)
            input_favorecido = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.css_inputfavorecido,
                )),
            )
            input_favorecido.click()
            sleep(1)
            input_favorecido.clear()

            input_favorecido.send_keys(
                self.bot_data.get("CNPJ_FAVORECIDO", "04.812.509/0001-90"),
            )

            result_favorecido = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.resultado_favorecido,
                )),
            )
            result_favorecido.click()
            self.driver.execute_script(
                f"document.querySelector('{el.css_inputfavorecido}').blur()",
            )

            self.message = "Informando centro de custas"
            self.type_log = "log"
            self.prt()

            sleep(1)

            centro_custas = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.css_centro_custas,
                )),
            )
            centro_custas.click()
            centro_custas.send_keys("A906030100")

            self.message = "Informando conta débito"
            self.type_log = "log"
            self.prt()

            div_conta_debito = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.css_div_conta_debito,
                )),
            )
            div_conta_debito.click()
            sleep(1)

            if solicitante == "jec":
                conta_debito = self.driver.find_element(
                    By.CSS_SELECTOR,
                    el.custas_civis,
                )
                conta_debito.click()

            elif solicitante == "monitoria" or solicitante == "monitória":
                conta_debito = self.driver.find_element(
                    By.CSS_SELECTOR,
                    el.custas_monitorias,
                )
                conta_debito.click()

        except ExecutionError as e:
            raise ExecutionError(exc=e) from e

    def save_changes(self) -> None:
        """Save all changes made during the payment process.

        Raises:
            ExecutionError: Erro de execução

        """
        try:
            self.message = "Salvando alterações"
            self.type_log = "log"
            self.prt()
            save = self.wait.until(
                ec.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    el.botao_salvar_pagamento,
                )),
            )
            save.click()

        except ExecutionError as e:
            raise ExecutionError(exc=e) from e

    def confirm_save(self) -> None:
        """Confirm the saving of payment details."""
        with suppress(Exception):
            tab_pagamentos = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.valor_pagamento,
                )),
            )
            tab_pagamentos.click()

            enter_table = (
                self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        el.valor_resultado,
                    )),
                )
                .find_element(By.TAG_NAME, "table")
                .find_element(By.TAG_NAME, "tbody")
            )
            check_solicitacoes = enter_table.find_elements(By.TAG_NAME, "tr")
            info_sucesso = [
                self.bot_data.get("NUMERO_PROCESSO"),
                "Pagamento solicitado com sucesso!!",
            ]
            current_handle = self.driver.current_window_handle

            for pos, item in enumerate(check_solicitacoes):
                if item.text == "Nenhum registro encontrado!":
                    _raise_execution_error(message="Pagamento não solicitado")

                sleep(2)
                open_details = item.find_element(
                    By.CSS_SELECTOR,
                    el.botao_ver,
                )
                open_details.click()

                sleep(1)
                id_task = item.find_elements(By.TAG_NAME, "td")[2].text
                close_context = self.wait.until(
                    ec.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            f'div[id="tabViewProcesso:pvp-dtProcessoValorResults:{pos}:pvp-pgBotoesValoresPagamentoBtnVer_dlg"]',
                        ),
                    ),
                ).find_element(By.TAG_NAME, "a")

                wait_frame = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        el.valor,
                    )),
                )
                self.driver.switch_to.frame(wait_frame)
                sleep(1)

                tipo_custa = ""
                cod_bars = ""
                tipo_condenacao = ""
                now = datetime.now(ZoneInfo("America/Manaus")).strftime(
                    "%d-%m-%Y %H.%M.%S",
                )
                nome_comprovante = f"COMPROVANTE 1 {self.bot_data.get('NUMERO_PROCESSO')} - {self.pid} - {now}.png"
                cod_bars_xls = str(
                    self.bot_data.get("COD_BARRAS")
                    .replace(".", "")
                    .replace(" ", ""),
                )

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
                    cod_bars = str(
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

                namedef = self.format_string(
                    self.bot_data.get("TIPO_PAGAMENTO"),
                ).lower()

                chk_bars = cod_bars == cod_bars_xls

                if namedef == "condenacao":
                    tipo_condenacao_xls = str(
                        self.bot_data.get("TIPO_CONDENACAO", ""),
                    )
                    match_condenacao = (
                        tipo_condenacao_xls.lower() == tipo_condenacao.lower()
                    )
                    matchs = all([match_condenacao, chk_bars])

                elif namedef == "custas":
                    tipo_custa_xls = str(self.bot_data.get("TIPO_GUIA", ""))
                    match_custa = tipo_custa_xls.lower() == tipo_custa.lower()
                    matchs = all([match_custa, chk_bars])

                if matchs:
                    self.driver.switch_to.default_content()
                    url_page = wait_frame.get_attribute("src")
                    self.screenshot_pagina(url_page, nome_comprovante)
                    self.driver.switch_to.window(current_handle)

                    close_context.click()
                    nome_comprovante2 = f"COMPROVANTE 2 {self.bot_data.get('NUMERO_PROCESSO')} - {self.pid} - {now}.png"
                    item.screenshot(
                        Path(self.output_dir_path).joinpath(nome_comprovante2),
                    )

                    info_sucesso.extend([
                        tipo_condenacao,
                        nome_comprovante,
                        id_task,
                        nome_comprovante2,
                    ])
                    return info_sucesso

                self.driver.switch_to.default_content()
                close_context.click()
                sleep(0.25)

            _raise_execution_error(message="Pagamento não solicitado")

        return [
            self.bot_data.get("NUMERO_PROCESSO"),
            "Pagamento solicitado com sucesso!!",
        ]

    def screenshot_pagina(self, url_page: str, nome_comprovante: str) -> None:
        """Capture a screenshot of the specified page.

        Args:
            url_page (str): The URL of the page to capture.
            nome_comprovante (str): The name for the screenshot file.

        """
        self.driver.switch_to.new_window("tab")
        self.driver.get(url_page)
        self.driver.save_screenshot(
            str(Path(self.output_dir_path).joinpath(nome_comprovante)),
        )
        self.driver.close()
