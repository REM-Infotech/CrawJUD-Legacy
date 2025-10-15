from contextlib import suppress
from time import sleep
from traceback import format_exception_only

from controllers.elaw import ElawBot
from resources.elements import elaw as el
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

type_doc = {"11": "cpf", "14": "cnpj"}


class ElawPartesPrincipais(ElawBot):
    def empresa(self) -> None:
        text = self.bot_data.get("EMPRESA")
        element_select: WebElement = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.empresa_input)),
        )

        message = "Informando Empresa"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select.select2(text)

        self.sleep_load('div[id="j_id_4p"]')

        message = "Empresa informada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def tipo_empresa(self) -> None:
        message = "Informando classificação da Empresa"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        key = "TIPO_EMPRESA"
        element_select = self.wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_CLASSIFICACAO_EMPRESA,
            )),
        )
        text = str(self.bot_data.get(key)).capitalize()

        element_select.select2(text)
        self.sleep_load('div[id="j_id_4p"]')

        message = "Classificação da Empresa informada"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        self.tipo_contingencia()

    def tipo_contingencia(self) -> None:
        wait = self.wait
        bot_data = self.bot_data

        message = "Informando contingenciamento"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        text = ["Passiva", "Passivo"]
        if str(bot_data.get("TIPO_EMPRESA")).lower() == "autor":
            text = ["Ativa", "Ativo"]

        select_contigencia: WebElement = wait.until(
            ec.presence_of_element_located((By.XPATH, el.contingencia)),
        )
        select_polo: WebElement = wait.until(
            ec.presence_of_element_located((By.XPATH, el.tipo_polo)),
        )

        select_contigencia.select2(text[0])
        self.sleep_load('div[id="j_id_4p"]')

        select_polo.select2(text[1])
        self.sleep_load('div[id="j_id_4p"]')

        message = "Contingenciamento informado!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def parte_contraria(self) -> None:
        message = "Preechendo informações da parte contrária"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)
        wait = self.wait
        text = self.bot_data.get("TIPO_PARTE_CONTRARIA")
        element_select: WebElement = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_TIPO_PARTE_CONTRARIA,
            )),
        )
        element_select.select2(text)

        doc_to_list = list(
            filter(
                lambda x: str.isdigit(x),
                ",".join(self.bot_data.get("DOC_PARTE_CONTRARIA")).split(","),
            ),
        )
        tipo_doc = type_doc.get(str(len(doc_to_list)))
        select_tipo_doc: WebElement = wait.until(
            ec.presence_of_element_located((By.XPATH, el.select_tipo_doc)),
        )
        select_tipo_doc.select2(tipo_doc)

        self.sleep_load('div[id="j_id_4p"]')
        campo_doc: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_campo_doc,
            )),
            message="Erro ao encontrar elemento",
        )
        campo_doc.click()
        sleep(0.05)
        campo_doc.clear()
        sleep(0.05)
        campo_doc.send_keys(self.bot_data.get("DOC_PARTE_CONTRARIA"))
        self.sleep_load('div[id="j_id_4p"]')

        search_button_parte: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_search_button,
            )),
            message="Erro ao encontrar elemento",
        )
        search_button_parte.click()
        self.sleep_load('div[id="j_id_4p"]')

        check_parte = self.check_part_found()

        if not check_parte:
            try:
                self.cadastro_parte_contraria()
                self.driver.switch_to.default_content()
                self.sleep_load('div[id="j_id_4p"]')

            except Exception:
                message = "Não foi possível cadastrar parte"
                _raise_execution_error(message=message)

        self.messsage = "Parte adicionada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def cadastro_parte_contraria(self) -> None:
        try:
            message = "Cadastrando parte"
            type_log = "log"
            self.print_msg(message=message, type_log=type_log, row=self.row)

            wait = self.wait
            driver = self.driver

            bot_data = self.bot_data

            add_parte: WebElement = wait.until(
                ec.presence_of_element_located((
                    By.XPATH,
                    el.parte_contraria,
                )),
                message="Erro ao encontrar elemento",
            )
            add_parte.click()

            self.sleep_load('div[id="j_id_4p"]')

            iframe = None

            main_window = driver.current_window_handle

            iframe: WebElement = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.iframe_cadastro_parte_contraria,
                )),
                message="Erro ao encontrar elemento",
            )
            link_iframe = iframe.get_attribute("src")
            driver.switch_to.new_window("tab")
            driver.get(link_iframe)
            sleep(0.5)
            with suppress(TimeoutException, NoSuchElementException):
                set_infomar_cpf: WebElement = (
                    wait.until(
                        ec.presence_of_element_located((
                            By.CSS_SELECTOR,
                            el.cpf_cnpj,
                        )),
                        message="Erro ao encontrar elemento",
                    )
                    .find_el(By.TAG_NAME, "td")[1]
                    .find_el(
                        By.CSS_SELECTOR,
                        el.botao_radio_widget,
                    )[1]
                )

                set_infomar_cpf.click()

            self.sleep_load('div[id="j_id_1o"]')
            doc_to_list = list(
                filter(
                    lambda x: str.isdigit(x),
                    ",".join(bot_data.get("DOC_PARTE_CONTRARIA")).split(","),
                ),
            )
            tipo_doc = type_doc.get(str(len(doc_to_list)), "cpf")
            select_tipo_doc = el.tipo_cpf_cnpj
            element_select: WebElement = wait.until(
                ec.presence_of_element_located((By.XPATH, select_tipo_doc)),
            )
            element_select.select2(tipo_doc.upper())

            sleep(2)
            self.sleep_load('div[id="j_id_1o"]')

            css_input_doc = el.tipo_cpf
            if tipo_doc == "cnpj":
                css_input_doc = el.tipo_cnpj

            input_doc: WebElement = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    css_input_doc,
                )),
                message="Erro ao encontrar elemento",
            )
            input_doc.click()
            sleep(0.05)
            input_doc.clear()
            input_doc.send_keys(bot_data.get("DOC_PARTE_CONTRARIA"))
            continuar = driver.find_element(
                By.CSS_SELECTOR,
                el.botao_parte_contraria,
            )
            continuar.click()

            self.sleep_load('div[id="j_id_1o"]')
            name_parte: WebElement = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.css_name_parte,
                )),
                message="Erro ao encontrar elemento",
            )
            name_parte.click()
            sleep(0.05)
            name_parte.send_keys(str(bot_data.get("PARTE_CONTRARIA")))
            driver.execute_script(
                f"document.querySelector('{el.css_name_parte}').blur()",
            )

            save_parte: WebElement = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.css_save_button,
                )),
                message="Erro ao encontrar elemento",
            )
            save_parte.click()

            message = "Parte cadastrada!"
            type_log = "info"
            self.print_msg(message=message, type_log=type_log, row=self.row)
            driver.close()

            driver.switch_to.window(main_window)

            element_close = el.iframe_cadastro_parte_close_dnv
            wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    element_close,
                )),
            ).click()

        except Exception as e:
            message = "\n".join(format_exception_only(e))
            _raise_execution_error(message=message)
