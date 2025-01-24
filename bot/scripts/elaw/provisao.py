import os
import pathlib
import time
from contextlib import suppress
from datetime import datetime
from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from ...common import ErroDeExecucao
from ...core import CrawJUD

# from ...shared import PropertiesCrawJUD

type_doc = {11: "cpf", 14: "cnpj"}


class provisao(CrawJUD):

    def __init__(self, *args, **kwrgs) -> None:
        super().__init__(*args, **kwrgs)

        # PropertiesCrawJUD.kwrgs = kwrgs
        # for key, value in list(kwrgs.items()):
        #     setattr(PropertiesCrawJUD, key, value)

        CrawJUD.setup()
        self.auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:

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
                        self.DriverLaunch(
                            message="Webdriver encerrado inesperadamente, reinicializando..."
                        )

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

    def queue(self) -> None | Exception:

        # module = "search_processo"

        try:
            search = self.search_bot()
            if search is True:

                self.type_log = "log"
                self.message = "Processo encontrado! Informando valores..."
                self.prt()

                calls = self.setup_calls()

                for call in calls:
                    call()

                self.save_changes()

            if search is False:
                raise ErroDeExecucao("Processo não encontrado!")

        except Exception as e:
            raise e

    def chk_risk(self):
        """
        Checks the risk label on the webpage and selects the appropriate risk type if the label indicates "Risco Quebrado".
        This method waits for the risk label element to be present on the webpage. If the label's text is "Risco Quebrado",
        it selects the risk type "Risco" from a dropdown menu.
        """

        label_risk = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.elements.type_risk_label)
            )
        )

        if label_risk.text == "Risco Quebrado":
            self.Select2_ELAW(self.elements.type_risk_select, "Risco")

    def setup_calls(self):

        calls = []

        # module = "get_valores_proc"
        get_valores = self.get_valores_proc()

        provisao = (
            str(self.bot_data.get("PROVISAO"))
            .replace("possivel", "possível")
            .replace("provavel", "provável")
            .lower()
        )

        chk_getvals1 = get_valores == "Contém valores"
        possible = provisao == "possível"

        if chk_getvals1 and possible:
            raise ErroDeExecucao('Provisão "Possível" já inserida')

        edit_button: WebElement = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.elements.css_btn_edit)
            )
        )
        edit_button.click()

        if get_valores == "Nenhum registro encontrado!":

            calls.append(self.add_new_valor)
            calls.append(self.edit_valor)
            calls.append(self.chk_risk)
            calls.append(self.set_valores)
            calls.append(self.informar_datas)

        elif get_valores == "Contém valores" or get_valores == "-":

            calls.append(self.edit_valor)
            calls.append(self.chk_risk)

            if provisao == "provável" or provisao == "possível":
                calls.append(self.set_valores)
                calls.append(self.informar_datas)

        calls.append(self.set_risk)
        calls.append(self.informar_motivo)

        return calls

    def get_valores_proc(self) -> str:

        get_valores: WebElement = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.elements.ver_valores))
        )
        get_valores.click()

        check_exists_provisao: WebElement = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.elements.table_valores_css)
            )
        )
        check_exists_provisao = check_exists_provisao.find_elements(By.TAG_NAME, "tr")

        for item in check_exists_provisao:
            item: WebElement = item

            valueprovisao = item.find_elements(By.TAG_NAME, "td")[0].text
            with suppress(NoSuchElementException):
                valueprovisao = item.find_element(
                    By.CSS_SELECTOR, self.elements.value_provcss
                ).text

            if "-" in valueprovisao or valueprovisao == "Nenhum registro encontrado!":
                return valueprovisao

        return "Contém valores"

    def add_new_valor(self):

        try:
            div_tipo_obj: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.div_tipo_obj_css)
                )
            )

            div_tipo_obj.click()

            item_obj_div: WebElement = (
                self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, self.elements.itens_obj_div_css)
                    )
                )
                .find_element(By.TAG_NAME, "ul")
                .find_elements(By.TAG_NAME, "li")[0]
                .find_element(By.CSS_SELECTOR, self.elements.checkbox)
            )

            item_obj_div.click()

            add_objeto = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.botao_adicionar
            )
            add_objeto.click()

            self.interact.sleep_load('div[id="j_id_7t"]')

        except Exception as e:
            raise ErroDeExecucao("Não foi possivel atualizar provisão", e=e)

    def edit_valor(self):

        editar_pedido: WebElement = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.elements.botao_editar)
            )
        )
        editar_pedido.click()

    def set_valores(self):

        try:

            self.message = "Informando valores"
            self.type_log = "log"
            self.prt()
            campo_valor_dml = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.css_val_inpt)
                )
            )

            campo_valor_dml.send_keys(Keys.CONTROL + "a")
            campo_valor_dml.send_keys(Keys.BACKSPACE)

            valor_informar = self.bot_data.get("VALOR_ATUALIZACAO")

            if isinstance(valor_informar, int):
                valor_informar = str(valor_informar) + ",00"

            elif isinstance(valor_informar, float):
                valor_informar = "{:.2f}".format(valor_informar).replace(".", ",")

            campo_valor_dml.send_keys(valor_informar)

            id_campo_valor_dml = campo_valor_dml.get_attribute("id")
            self.driver.execute_script(
                f"document.getElementById('{id_campo_valor_dml}').blur()"
            )
        except Exception as e:
            raise e

    def set_risk(self):

        try:

            self.message = "Alterando risco"
            self.type_log = "log"
            self.prt()

            expand_filter_risk = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.css_risk)
                )
            )
            expand_filter_risk.click()

            div_filter_risk = self.driver.find_element(
                By.CSS_SELECTOR,
                self.elements.processo_objt,
            )
            filter_risk = div_filter_risk.find_elements(By.TAG_NAME, "li")

            for item in filter_risk:

                # label_risco = self.driver.find_element(By.CSS_SELECTOR, 'label[id="j_id_2m:j_id_2p_2e:processoAmountObjetoDt:0:j_id_2p_2i_5_1_6_5_k_2_2_1_label"]').text.lower()
                provisao_from_xlsx = (
                    str(self.bot_data.get("PROVISAO"))
                    .lower()
                    .replace("possivel", "possível")
                    .replace("provavel", "provável")
                )

                provisao = item.text.lower()
                if provisao == provisao_from_xlsx:
                    sleep(1)
                    item.click()
                    break

            id_expand_filter = expand_filter_risk.get_attribute("id")
            self.driver.execute_script(
                f"document.getElementById('{id_expand_filter}').blur()"
            )

            self.interact.sleep_load('div[id="j_id_2z"]')

        except Exception as e:
            raise e

    def informar_datas(self):

        try:

            self.message = "Alterando datas de correção base e juros"
            self.type_log = "log"
            self.prt()

            def set_dataCorrecao(dataBaseCorrecao: str):

                DataCorrecao = self.driver.find_element(
                    By.CSS_SELECTOR, self.elements.DataCorrecaoCss
                )
                css_DataCorrecao = DataCorrecao.get_attribute("id")
                self.interact.clear(DataCorrecao)
                self.interact.send_key(DataCorrecao, dataBaseCorrecao)

                self.driver.execute_script(
                    f"document.getElementById('{css_DataCorrecao}').blur()"
                )
                self.interact.sleep_load('div[id="j_id_2z"]')

            def set_DataJuros(dataBaseJuros: str):

                DataJuros = self.driver.find_element(
                    By.CSS_SELECTOR, self.elements.DataJurosCss
                )
                css_data = DataJuros.get_attribute("id")
                self.interact.clear(DataJuros)
                self.interact.send_key(DataJuros, dataBaseJuros)
                self.driver.execute_script(
                    f"document.getElementById('{css_data}').blur()"
                )
                self.interact.sleep_load('div[id="j_id_2z"]')

            dataBaseCorrecao = self.bot_data.get("DATA_BASE_CORRECAO")
            dataBaseJuros = self.bot_data.get("DATA_BASE_JUROS")
            if dataBaseCorrecao is not None:

                if isinstance(dataBaseCorrecao, datetime):
                    dataBaseCorrecao = dataBaseCorrecao.strftime("%d/%m/%Y")

                set_dataCorrecao(dataBaseCorrecao)

            if dataBaseJuros is not None:

                if isinstance(dataBaseJuros, datetime):
                    dataBaseJuros = dataBaseJuros.strftime("%d/%m/%Y")

                set_DataJuros(dataBaseJuros)

        except Exception as e:
            raise e

    def informar_motivo(self):

        try:
            try_salvar = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.botao_salvar_id
            )

            sleep(1)
            try_salvar.click()

            self.interact.sleep_load('div[id="j_id_2z"]')

            self.message = "Informando justificativa"
            self.type_log = "log"
            self.prt()
            informar_motivo: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        self.elements.texto_motivo,
                    )
                )
            )
            informar_motivo.send_keys(
                self.bot_data.get("OBSERVACAO", "Atualização de provisão")
            )
            id_informar_motivo = informar_motivo.get_attribute("id")
            self.driver.execute_script(
                f"document.getElementById('{id_informar_motivo}').blur()"
            )

        except Exception as e:
            raise e

    def save_changes(self) -> None:

        self.interact.sleep_load('div[id="j_id_2z"]')
        salvar = self.driver.find_element(
            By.CSS_SELECTOR, self.elements.botao_salvar_id
        )
        salvar.click()

        check_provisao_atualizada = None
        with suppress(TimeoutException):
            check_provisao_atualizada: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#valoresGeralPanel_header > span")
                )
            )

        if not check_provisao_atualizada:
            raise ErroDeExecucao("Não foi possivel atualizar provisão")

        comprovante = self.print_comprovante()
        data = [
            str(self.bot_data.get("NUMERO_PROCESSO")),
            comprovante,
            "Provisão atualizada com sucesso!",
        ]
        self.append_success(data, message="Provisão atualizada com sucesso!")

    def print_comprovante(self) -> str:

        name_comprovante = f'Comprovante Cadastro - {self.bot_data.get("NUMERO_PROCESSO")} - PID {self.pid}.png'
        savecomprovante = os.path.join(
            pathlib.Path(__file__).cwd(), "exec", self.pid, name_comprovante
        )
        self.driver.get_screenshot_as_file(savecomprovante)
        return name_comprovante
