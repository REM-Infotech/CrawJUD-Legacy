import os
import time
from contextlib import suppress
from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from bot.common.exceptions import ErroDeExecucao
from bot.meta.CrawJUD import CrawJUD

type_doc = {11: "cpf", 14: "cnpj"}


class provisao(CrawJUD):

    def __init__(self, **kwrgs) -> None:
        super().__init__(**kwrgs)
        super().auth_bot()
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
                    super().auth_bot()

            try:
                self.queue()

            except Exception as e:

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

        search = self.SearchBot()
        if search is True:

            self.type_log = "log"
            self.message = "Processo encontrado! Informando valores..."
            self.prt()
            # module = "get_valores_proc"
            get_valores = self.get_valores_proc()

            edit_button: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.css_btn_edit)
                )
            )
            edit_button.click()
            provisao = (
                str(self.bot_data.get("PROVISAO"))
                .replace("possivel", "possível")
                .lower()
            )

            chk_getvals1 = get_valores == "Contém valores"
            not_possible = provisao != "possível"
            if get_valores == "Nenhum registro encontrado!":

                # module = "add_new_valor"
                self.add_new_valor()

                # module = "set_valores"
                self.set_valores()

                self.save_changes()

            elif "-" in get_valores or chk_getvals1 and not_possible:

                # module = "set_valores"
                self.set_valores()
                self.save_changes()

            elif get_valores == "Contém valores" and provisao == "possível":

                self.message = 'Provisão "Possível" já inserida'
                self.type_log = "error"
                self.prt()
                self.append_error([self.bot_data.get("NUMERO_PROCESSO"), self.message])

        if search is not True:
            self.message = "Processo não encontrado!"
            self.type_log = "error"
            self.prt()
            self.append_error([self.bot_data.get("NUMERO_PROCESSO"), self.message])

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

    def add_new_valor(self) -> None | Exception:

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

    def set_valores(self) -> None | Exception:

        try:
            editar_pedido: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.botao_editar)
                )
            )
            editar_pedido.click()

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

            valor_informar = str(self.bot_data.get("VALOR_ATUALIZACAO"))

            if "," in valor_informar:
                sleep(0.25)
                campo_valor_dml.send_keys(f"{valor_informar}")
            elif "," not in valor_informar:
                sleep(0.25)
                campo_valor_dml.send_keys(f"{valor_informar}{','}")

            id_campo_valor_dml = campo_valor_dml.get_attribute("id")
            self.driver.execute_script(
                f"document.getElementById('{id_campo_valor_dml}').blur()"
            )

            expand_filter_risk = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.css_risk
            )
            expand_filter_risk.click()

            div_filter_risk = self.driver.find_element(
                By.CSS_SELECTOR,
                self.elements.processo_objt,
            )
            filter_risk = div_filter_risk.find_elements(By.TAG_NAME, "li")

            self.message = "Alterando risco"
            self.type_log = "log"
            self.prt()
            for item in filter_risk:

                # label_risco = self.driver.find_element(By.CSS_SELECTOR, 'label[id="j_id_2m:j_id_2p_2e:processoAmountObjetoDt:0:j_id_2p_2i_5_1_6_5_k_2_2_1_label"]').text.lower()
                provisao_from_xlsx = str(self.bot_data.get("PROVISAO")).lower()

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

            try_salvar = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.botao_salvar_id
            )

            if str(self.bot_data.get("PROVISAO")).lower() != "possível":

                self.message = "Alterando datas de correção base e juros"
                self.type_log = "log"
                self.prt()
                if self.bot_data.get("DATA_ATUALIZACAO"):

                    DataCorrecao = self.driver.find_element(
                        By.CSS_SELECTOR, self.elements.DataCorrecaoCss
                    )
                    css_DataCorrecao = DataCorrecao.get_attribute("id")
                    self.interact.clear(DataCorrecao)
                    self.interact.send_key(
                        DataCorrecao, self.bot_data.get("DATA_ATUALIZACAO")
                    )

                    self.driver.execute_script(
                        f"document.getElementById('{css_DataCorrecao}').blur()"
                    )
                    self.interact.sleep_load('div[id="j_id_2z"]')

                    DataJuros = self.driver.find_element(
                        By.CSS_SELECTOR, self.elements.DataJurosCss
                    )
                    css_data = DataJuros.get_attribute("id")
                    self.interact.clear(DataJuros)
                    self.interact.send_key(
                        DataJuros, self.bot_data.get("DATA_ATUALIZACAO")
                    )
                    self.driver.execute_script(
                        f"document.getElementById('{css_data}').blur()"
                    )
                    self.interact.sleep_load('div[id="j_id_2z"]')

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
                f"Atualização de provisão - {self.bot_data.get('OBSERVACAO')}"
            )
            id_informar_motivo = informar_motivo.get_attribute("id")
            self.driver.execute_script(
                f"document.getElementById('{id_informar_motivo}').blur()"
            )

        except Exception as e:
            raise ErroDeExecucao(e=e)

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
        savecomprovante = os.path.join(os.getcwd(), "Temp", self.pid, name_comprovante)
        self.driver.get_screenshot_as_file(savecomprovante)
        return name_comprovante
