"""Modulo Elaw Pré Cadastro."""

from __future__ import annotations

import time
from contextlib import suppress
from time import sleep
from typing import TYPE_CHECKING

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.bots.elaw.cadastro import ElawCadastro
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task
from crawjud.decorators.bot import wrap_cls
from crawjud.resources.elements import elaw as el

if TYPE_CHECKING:
    from crawjud.utils.webdriver.web_element import WebElementBot as WebElement

type_doc = {"11": "cpf", "14": "cnpj"}


@shared_task(name="elaw.cadastro", bind=True, context=ContextTask)
@wrap_cls
class Cadastro(ElawCadastro):
    """The Cadastro class extends CrawJUD to manage registration tasks within the application.

    Attributes:
        type_doc (dict): A dictionary mapping document types to their identifiers.
        ...existing attributes...

    """

    def execution(self) -> None:
        """Execute the main processing loop for registrations.

        Iterates over each entry in the data frame and processes it.
        Handles authentication and error logger.

        """
        frame = self.frame
        self.total_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = self.elaw_formats(value)
            self.queue()

        self.finalize_execution()

    def queue(self) -> None:
        try:
            driver = self.driver
            search = self.search(bot_data=self.bot_data)

            if search:
                message = "Processo já cadastrado!"
                type_log = "error"
                self.print_msg(
                    message=message,
                    type_log=type_log,
                    row=self.row,
                )
                self.append_success()
                return

            message = "Processo não encontrado, inicializando cadastro..."
            type_log = "log"
            self.print_msg(
                message=message,
                type_log=type_log,
                row=self.row,
            )

            btn_newproc = driver.find_element(
                By.CSS_SELECTOR,
                el.botao_novo,
            )
            btn_newproc.click()

            start_time = time.perf_counter()

            self.area_direito()
            self.subarea_direito()
            self.next_page()
            self.info_localizacao()
            self.informa_estado()
            self.informa_comarca()
            self.informa_foro()
            self.informa_vara()
            self.informa_proceso()
            self.informa_empresa()
            self.set_classe_empresa()
            self.parte_contraria()
            self.uf_proc()
            self.acao_proc()
            self.advogado_interno()
            self.adv_parte_contraria()
            self.data_distribuicao()
            self.info_valor_causa()
            self.escritorio_externo()
            self.tipo_contingencia()

            end_time = time.perf_counter()
            execution_time = end_time - start_time
            calc = execution_time / 60
            splitcalc = str(calc).split(".")
            minutes = int(splitcalc[0])
            seconds = int(float(f"0.{splitcalc[1]}") * 60)

            message = f"Formulário preenchido em {minutes} minutos e {seconds} segundos"
            type_log = "log"
            self.print_msg(
                message=message,
                type_log=type_log,
                row=self.row,
            )

            self.salvar_tudo()

            if self.confirm_save() is True:
                self.print_comprovante()

        except Exception as e:
            self.append_error(exc=e)

    def informa_proceso(self) -> None:
        key = "NUMERO_PROCESSO"
        css_campo_processo = el.numero_processo

        message = "Informando número do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        campo_processo: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                css_campo_processo,
            )),
            message="Erro ao encontrar elemento",
        )
        campo_processo.click()

        self.interact.send_key(campo_processo, self.bot_data.get(key))

        self.driver.execute_script(
            f'document.querySelector("{css_campo_processo}").blur()',
        )
        self.sleep_load('div[id="j_id_4b"]')

        message = "Número do processo informado!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def informa_empresa(self) -> None:
        text = self.bot_data.get("EMPRESA")
        element_select: WebElement = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.empresa_input)),
        )

        message = "Informando Empresa"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select.select2(text)

        self.sleep_load('div[id="j_id_4b"]')

        message = "Empresa informada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def set_classe_empresa(self) -> None:
        key = "TIPO_EMPRESA"
        element_select = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.tipo_empresa_input)),
        )
        text = str(self.bot_data.get(key)).capitalize()

        message = "Informando classificação da Empresa"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select.select2(text)
        self.sleep_load('div[id="j_id_4b"]')

        message = "Classificação da Empresa informada"
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
                el.tipo_parte_contraria_input,
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

        self.sleep_load('div[id="j_id_4b"]')
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
        self.interact.send_key(
            campo_doc,
            self.bot_data.get("DOC_PARTE_CONTRARIA"),
        )
        self.sleep_load('div[id="j_id_4b"]')

        search_button_parte: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_search_button,
            )),
            message="Erro ao encontrar elemento",
        )
        search_button_parte.click()
        self.sleep_load('div[id="j_id_4b"]')

        check_parte = self.check_part_found()

        if not check_parte:
            try:
                self.cadastro_parte_contraria()
                self.driver.switch_to.default_content()
                self.sleep_load('div[id="j_id_4b"]')

            except Exception as e:
                raise ExecutionError(
                    message="Não foi possível cadastrar parte",
                    e=e,
                ) from e

        self.messsage = "Parte adicionada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def uf_proc(self) -> None:
        message = "Preenchendo UF Processo..."
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)
        element_select: WebElement = self.driver.find_element(
            By.XPATH,
            el.select_uf_proc,
        )
        text = str(self.bot_data.get("CAPITAL_INTERIOR"))
        element_select.select2(text)
        sleep(0.5)

        self.sleep_load('div[id="j_id_4b"]')

        if (
            str(self.bot_data.get("CAPITAL_INTERIOR")).lower()
            == "outro estado"
        ):
            other_location: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.css_other_location,
                )),
                message="Erro ao encontrar elemento",
            )
            other_location.click()
            self.interact.send_key(other_location, self.bot_data.get("ESTADO"))
            self.interact.send_key(other_location, Keys.ENTER)

    def acao_proc(self) -> None:
        message = "Informando ação do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        div_comboProcessoTipo: WebElement = self.wait.until(  # noqa: N806
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.comboProcessoTipo,
            )),
            message="Erro ao encontrar elemento",
        )
        div_comboProcessoTipo.click()

        elemento = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.filtro_processo,
            )),
            message="Erro ao encontrar elemento",
        )

        text = self.bot_data.get("ACAO")
        self.interact.click(elemento)
        self.interact.send_key(elemento, text)
        self.interact.send_key(elemento, Keys.ENTER)
        self.sleep_load('div[id="j_id_4b"]')

        message = "Ação informada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def data_distribuicao(self) -> None:
        self.sleep_load('div[id="j_id_4b"]')
        message = "Informando data de distribuição"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        self.sleep_load('div[id="j_id_4b"]')
        data_distribuicao: WebElement = self.wait.until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                el.css_data_distribuicao,
            )),
            message="Erro ao encontrar elemento",
        )

        self.interact.clear(data_distribuicao)

        self.interact.send_key(
            data_distribuicao,
            self.bot_data.get("DATA_DISTRIBUICAO"),
        )
        self.interact.send_key(data_distribuicao, Keys.TAB)
        self.sleep_load('div[id="j_id_4b"]')

        message = "Data de distribuição informada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def adv_parte_contraria(self) -> None:
        driver = self.driver
        wait = self.wait

        bot_data = self.bot_data
        message = "Informando Adv. Parte contrária"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        campo_adv: WebElement = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_input_adv,
            )),
            message="Erro ao encontrar elemento",
        )
        campo_adv.click()
        campo_adv.clear()
        sleep(0.02)

        text = str(bot_data.get("ADV_PARTE_CONTRARIA"))

        for i in ["\t", "\n"]:
            if i in text:
                text = text.split(i)[0]
                break

        campo_adv.send_keys(text)

        check_adv = None

        self.sleep_load('div[id="j_id_4b"]')

        with suppress(TimeoutException):
            check_adv = (
                WebDriverWait(driver, 15)
                .until(
                    ec.presence_of_element_located((
                        By.XPATH,
                        el.css_check_adv,
                    )),
                    message="Erro ao encontrar elemento",
                )
                .text
            )
            campo_adv.send_keys(Keys.ENTER)

            element_campo_adv_outraparte = (
                f'input[id="{campo_adv.get_attribute("id")}"]'
            )

            driver.execute_script(
                f"document.querySelector('{element_campo_adv_outraparte}').blur()",
            )

            self.sleep_load('div[id="j_id_4b"]')

            message = "Adv. parte contrária informado!"
            type_log = "info"
            self.print_msg(message=message, type_log=type_log, row=self.row)

            return

        if not check_adv:
            self.cadastro_advogado_contra()
            driver.switch_to.default_content()

        self.sleep_load('div[id="j_id_4b"]')

        message = "Adv. parte contrária informado!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def info_valor_causa(self) -> None:
        """Inform the value of the cause.

        This method retrieves the cause value from the bot data, inputs it into the
        designated field, and logs the action performed.



        """
        wait = self.wait
        driver = self.driver

        bot_data = self.bot_data

        message = "Informando valor da causa"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        valor_causa: WebElement = wait.until(
            ec.presence_of_element_located((By.XPATH, el.valor_causa)),
            message="Erro ao encontrar elemento",
        )

        valor_causa.click()
        sleep(0.5)
        valor_causa.clear()
        id_valor_causa = valor_causa.get_attribute("id")
        input_valor_causa = f'input[id="{id_valor_causa}"]'
        valor_causa.send_keys(bot_data.get("VALOR_CAUSA"))

        driver.execute_script(
            f"document.querySelector('{input_valor_causa}').blur()",
        )

        self.sleep_load('div[id="j_id_4b"]')

        message = "Valor da causa informado!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def escritorio_externo(self) -> None:
        """Inform the external office involved in the process.

        This method retrieves the external office information from the bot data,
        inputs it into the designated field, and logs the action performed.



        """
        wait = self.wait
        bot_data = self.bot_data

        message = "Informando Escritório Externo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        div_escritrorioexterno: WebElement = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.escritrorio_externo,
            )),
            message="Erro ao encontrar elemento",
        )
        div_escritrorioexterno.click()
        sleep(1)

        text = bot_data.get("ESCRITORIO_EXTERNO")
        select_escritorio: WebElement = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.select_escritorio,
            )),
        )
        select_escritorio.select2(text)
        self.sleep_load('div[id="j_id_4b"]')

        message = "Escritório externo informado!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

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
        self.sleep_load('div[id="j_id_4b"]')

        select_polo.select2(text[1])
        self.sleep_load('div[id="j_id_4b"]')

        message = "Contingenciamento informado!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def cadastro_advogado_contra(self) -> None:
        try:
            wait = self.wait
            driver = self.driver

            bot_data = self.bot_data

            message = "Cadastrando advogado"
            type_log = "log"
            self.print_msg(message=message, type_log=type_log, row=self.row)

            add_parte: WebElement = wait.until(
                ec.presence_of_element_located((
                    By.XPATH,
                    el.btn_novo_advogado_contra,
                )),
                message="Erro ao encontrar elemento",
            )
            add_parte.click()

            self.sleep_load('div[id="j_id_4b"]')

            main_window = driver.current_window_handle

            iframe: WebElement = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.iframe_cadastro_advogado_contra,
                )),
                message="Erro ao encontrar elemento",
            )
            link_iframe = iframe.get_attribute("src")
            driver.switch_to.new_window("tab")
            driver.get(link_iframe)

            sleep(0.5)

            naoinfomadoc: WebElement = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.css_naoinfomadoc,
                )),
                message="Erro ao encontrar elemento",
            )
            naoinfomadoc.click()

            sleep(0.5)
            continuebutton: WebElement = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.botao_continuar,
                )),
                message="Erro ao encontrar elemento",
            )
            continuebutton.click()

            self.sleep_load('div[id="j_id_1o"]')
            sleep(0.5)

            input_nomeadv: WebElement = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.css_input_nomeadv,
                )),
                message="Erro ao encontrar elemento",
            )
            input_nomeadv.click()
            input_nomeadv.send_keys(bot_data.get("ADV_PARTE_CONTRARIA"))

            driver.execute_script(
                f"document.querySelector('{el.css_input_nomeadv}').blur()",
            )

            sleep(0.05)
            salvar: WebElement = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.salvarcss,
                )),
                message="Erro ao encontrar elemento",
            )
            salvar.click()

            message = "Advogado cadastrado!"
            type_log = "info"
            self.print_msg(message=message, type_log=type_log, row=self.row)

            driver.close()
            driver.switch_to.window(main_window)

            wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.iframe_cadastro_advogado_close_dnv,
                )),
            )

            self.sleep_load('div[id="j_id_4b"]')

        except Exception as e:
            raise ExecutionError(
                message="Não foi possível cadastrar advogado",
                e=e,
            ) from e

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

            self.sleep_load('div[id="j_id_4b"]')

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
            raise ExecutionError(e=e) from e

    def check_part_found(self) -> str | None:
        name_parte = None
        tries: int = 0

        driver = self.driver

        while tries < 4:
            with suppress(NoSuchElementException):
                name_parte = (
                    driver.find_element(
                        By.CSS_SELECTOR,
                        el.css_t_found,
                    )
                    .find_element(By.TAG_NAME, "td")
                    .text
                )

            if name_parte:
                break

            sleep(1)
            tries += 1

        return name_parte
