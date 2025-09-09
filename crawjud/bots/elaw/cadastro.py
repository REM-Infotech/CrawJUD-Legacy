"""Module for managing new registrations in the ELAW system.

This module handles the creation and management of new registrations within the ELAW system.
It automates the process of entering new records and their associated data.

Classes:
    Cadastro: Manages new registrations by extending the CrawJUD base class

Attributes:
    type_doc (dict): Maps document lengths to document types (CPF/CNPJ)

"""

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

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.elaw import ElawBot
from crawjud.custom.task import ContextTask
from crawjud.decorators import shared_task
from crawjud.decorators.bot import wrap_cls
from crawjud.resources.elements import elaw as el

if TYPE_CHECKING:
    from crawjud.utils.webdriver.web_element import WebElementBot as WebElement

type_doc = {"11": "cpf", "14": "cnpj"}


@shared_task(name="elaw.cadastro", bind=True, context=ContextTask)
@wrap_cls
class Cadastro(ElawBot):
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
        """Handle the registration queue processing.

        Refreshes the driver, extracts process information, and manages the registration
        process using the ELAW system. Logs the steps, calculates execution time,
        and handles potential exceptions.
        """
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

    def area_direito(self) -> None:
        """Select the area of law in the web form.

        This method interacts with a web form to select the area of law specified
        in the bot data. It logs the process and handles any necessary waits and
        interactions with the web el.


        """
        wait = self.wait
        message = "Informando área do direito"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)
        text = str(self.bot_data.get("AREA_DIREITO"))
        sleep(0.5)

        element_area_direito: WebElement = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.css_label_area,
            )),
        )
        element_area_direito.select2(text)
        self.sleep_load('div[id="j_id_47"]')

        message = "Área do direito selecionada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def subarea_direito(self) -> None:
        """Select the sub-area of law in the web form.

        This method interacts with a web form to select the sub-area of law specified
        in the bot data. It logs the process and handles any necessary waits and
        interactions with the web el.
        """
        wait = self.wait
        message = "Informando sub-área do direito"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        text = str(self.bot_data.get("SUBAREA_DIREITO"))
        sleep(0.5)

        element_subarea: WebElement = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.comboareasub_css,
            )),
        )
        element_subarea.select2(text)

        self.sleep_load('div[id="j_id_4b"]')
        message = "Sub-Área do direito selecionada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def next_page(self) -> None:
        """Navigate to the next page by clicking the designated button.

        This method waits until the next page button is present in the DOM,
        then clicks it to navigate to the next page.

        """
        next_page: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_button,
            )),
            message="Erro ao encontrar elemento",
        )
        next_page.click()

    def info_localizacao(self) -> None:
        """Provide information about the location of the process.

        This method selects the judicial sphere of the process and logs the actions performed.
        It interacts with the web el to set the sphere and waits for the loading to complete.

        """
        text = "Judicial"

        message = "Informando esfera do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select: WebElement = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.css_esfera_judge)),
        )

        element_select.select2(text)
        self.sleep_load('div[id="j_id_4b"]')

        message = "Esfera Informada!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def informa_estado(self) -> None:
        """Informs the state of the process by selecting the appropriate option from a dropdown menu.

        This method retrieves the state information from the bot's data, logs the action,
        selects the state in the dropdown menu using the select2 method, waits for the
        page to load, and then logs the completion of the action.


        """
        key = "ESTADO"

        text = str(self.bot_data.get(key, None))

        message = "Informando estado do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select: WebElement = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.estado_input)),
        )

        element_select.select2(text)
        self.sleep_load('div[id="j_id_4b"]')

        message = "Estado do processo informado!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def informa_comarca(self) -> None:
        """Fill in the comarca (judicial district) information for the process.

        This method retrieves the comarca information from the bot data, selects the appropriate
        input element, and inputs the comarca text. It also logs the actions performed.
        Steps:
        1. Retrieve the comarca information from crawjud.bot data.
        2. Select the comarca input element.
        3. Log the action of informing the comarca.
        4. Use the select2 method to input the comarca text.
        5. Wait for the loading indicator to disappear.
        6. Log the completion of the comarca information input.


        """
        text = str(self.bot_data.get("COMARCA"))

        message = "Informando comarca do processo"
        type_log = "log"

        element_select: WebElement = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.comarca_input)),
        )
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select.select2(text)
        self.sleep_load('div[id="j_id_4b"]')

        message = "Comarca do processo informado!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def informa_foro(self) -> None:
        """Informs the court jurisdiction (foro) for the process.

        This method retrieves the court jurisdiction information from the bot data,
        logs the action, and interacts with the web element to input the court jurisdiction.
        Steps:
        1. Retrieves the court jurisdiction from `self.bot_data`.
        2. Logs the action of informing the court jurisdiction.
        3. Uses the `select2` method to select the court jurisdiction in the web element.
        4. Waits for the loading element to disappear.
        5. Logs the completion of the action.


        """
        text = str(self.bot_data.get("FORO"))

        message = "Informando foro do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select: WebElement = self.wait.until(
            ec.presence_of_element_located((By.XPATH, el.foro_input)),
        )
        element_select.select2(text)
        self.sleep_load('div[id="j_id_4b"]')

        message = "Foro do processo informado!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def informa_vara(self) -> None:
        """Fill in the court information for the process.

        This method retrieves the court information from the bot data and inputs it
        into the appropriate field in the ELAW system. It logs the actions performed
        and ensures the input is processed by the system.
        Steps:
        1. Retrieve the court information from `self.bot_data`.
        2. Log the action of informing the court information.
        3. Use the `select2` method to input the court information.
        4. Wait for the system to process the input.
        5. Log the completion of the action.



        """
        text = self.bot_data.get("VARA")

        wait = self.wait
        message = "Informando vara do processo"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        element_select: WebElement = wait.until(
            ec.presence_of_element_located((By.XPATH, el.vara_input)),
        )

        element_select.select2(text)

        self.sleep_load('div[id="j_id_4b"]')

        message = "Vara do processo informado!"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def informa_proceso(self) -> None:
        """Inform the process number in the web form.

        This method retrieves the process number from the bot data, inputs it into the
        designated field, and handles any necessary interactions and waits.

        """
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
        """Inform the company associated with the process.

        This method retrieves the company name from the bot data, selects the appropriate
        input field, and inputs the company name. It includes logging of actions performed.



        """
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
        """Set the classification of the company.

        This method retrieves the company type from the bot data, formats it,
        and uses it to interact with a specific input element on the page.
        It logs messages before and after the interaction to indicate the
        progress of the operation.



        """
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
        """Handle the opposing party information.

        This method manages the input and processing of opposing party details.
        It interacts with the relevant web el and ensures the data is correctly
        entered and processed.

        Raises:
            ExecutionError: If an error occurs during the process.

        """
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
        """Inform the federal unit (state) of the process.

        This method selects the appropriate state from the dropdown menu based on
        the bot data and logs the action performed.



        """
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
        """Inform the action of the process.

        This method selects the appropriate action type for the process from the
        dropdown menu based on the bot data and logs the action performed.



        """
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
        """Inform the distribution date of the process.

        This method inputs the distribution date into the designated field and logs
        the action performed.



        """
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

    def advogado_interno(self) -> None:
        """Inform the internal lawyer.

        This method inputs the internal lawyer information into the system
        and ensures it is properly selected.

        Raises:
            ExecutionError: Erro caso advogado não seja encontrado

        """
        wait = self.wait
        driver = self.driver

        bot_data = self.bot_data

        message = "informando advogado interno"
        type_log = "log"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        input_adv_responsavel: WebElement = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.adv_responsavel,
            )),
        )
        input_adv_responsavel.click()
        input_adv_responsavel.send_keys(
            bot_data.get("ADVOGADO_INTERNO"),
        )

        id_input_adv = input_adv_responsavel.get_attribute("id").replace(
            "_input",
            "_panel",
        )
        css_wait_adv = f"span[id='{id_input_adv}'] > ul > li"

        wait_adv = None

        with suppress(TimeoutException):
            wait_adv: WebElement = WebDriverWait(driver, 25).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    css_wait_adv,
                )),
            )

        if wait_adv:
            wait_adv.click()
        elif not wait_adv:
            raise ExecutionError(message="Advogado interno não encontrado")

        self.sleep_load('div[id="j_id_4b"]')

        self.sleep_load('div[id="j_id_4b"]')
        element_select: WebElement = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.select_advogado_responsavel,
            )),
        )
        element_select.select2(bot_data.get("ADVOGADO_INTERNO"))

        id_element = element_select.get_attribute("id")
        id_input_css = f'[id="{id_element}"]'
        comando = f"document.querySelector('{id_input_css}').blur()"
        driver.execute_script(comando)

        self.sleep_load('div[id="j_id_4b"]')

        message = "Advogado interno informado!"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

    def adv_parte_contraria(self) -> None:
        """Inform the lawyer for the opposing party.

        This method retrieves the opposing party's lawyer information from the bot data,
        inputs it into the designated field, and logs the action performed.

        """
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
        """Inform the type of contingency for the process.

        This method selects the appropriate contingency type from the dropdown menu
        based on the bot data and logs the action performed.



        """
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
        """Register the lawyer information.

        This method handles the registration of lawyer details by interacting with
        the relevant web el and logging the actions performed.

        Raises:
            ExecutionError: If an error occurs during the process.

        """
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
        """Register the party information.

        This method handles the registration of party details by interacting with
        the relevant web el and logging the actions performed.

        Raises:
            ExecutionError: If an error occurs during the process

        """
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

    def salvar_tudo(self) -> None:
        """Save all entered information.

        This method clicks the save button to persist all entered data and logs the
        action performed.



        """
        wait = self.wait

        self.sleep_load('div[id="j_id_4b"]')
        salvartudo: WebElement = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.css_salvar_proc,
            )),
            message="Erro ao encontrar elemento",
        )

        message = "Salvando processo novo"
        type_log = "info"
        self.print_msg(message=message, type_log=type_log, row=self.row)

        salvartudo.click()

    def check_part_found(self) -> str | None:
        """Check if the opposing party is found.

        This method verifies the presence of the opposing party in the process.
        It interacts with the web el to perform the check and returns the result.

        Args:
            driver: The WebDriver instance.

        Returns:
            str | None: The status of the opposing party search.

        """
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

    def confirm_save(self) -> bool:
        """Confirm the saving of information.

        This method verifies that all information has been successfully saved
        by checking the URL and interacting with web el as needed.
        Logs the action performed.

        Returns:
            bool: True if the save is confirmed, False otherwise.

        Raises:
            ExecutionError: If the save confirmation fails.

        """
        wait = self.wait
        driver = self.driver

        with suppress(TimeoutException):
            WebDriverWait(driver, 20).until(
                ec.url_to_be("https://amazonas.elaw.com.br/processoView.elaw"),
                message="Erro ao encontrar elemento",
            )

            self.print_msg(
                message="Processo salvo com sucesso!",
                type_log="log",
                row=self.row,
            )
            return True

        mensagem_erro: str = None
        with suppress(TimeoutException, NoSuchElementException):
            mensagem_erro = (
                wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        el.div_messageerro_css,
                    )),
                    message="Erro ao encontrar elemento",
                )
                .find_element(By.TAG_NAME, "ul")
                .text
            )

        if not mensagem_erro:
            mensagem_erro = (
                "Cadastro do processo nao finalizado, verificar manualmente"
            )

        raise ExecutionError(mensagem_erro)
