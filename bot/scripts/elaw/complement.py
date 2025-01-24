import os
import pathlib
import time
from contextlib import suppress
from time import sleep
from typing import Callable, Dict, List, Self

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from ...common import ErroDeExecucao
from ...core import CrawJUD
from ...shared import PropertiesCrawJUD

type_doc = {11: "cpf", 14: "cnpj"}

campos_validar: List[str] = [
    "estado",
    "comarca",
    "foro",
    "vara",
    "divisao",
    "fase",
    "provimento",
    "fato_gerador",
    "objeto",
    "tipo_empresa",
    "tipo_entrada",
    "acao",
    "escritorio",
    "classificacao",
    "toi_criado",
    "nota_tecnica",
    "liminar",
]


class complement(PropertiesCrawJUD):

    def __init__(self, *args, **kwrgs) -> None:
        super().__init__(*args, **kwrgs)
        CrawJUD.setup()
        CrawJUD.auth_bot()
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
                    CrawJUD.auth_bot()

            try:
                self.queue()

            except Exception as e:

                old_message = None
                windows = self.driver.window_handles

                if len(windows) == 0:
                    with suppress(Exception):
                        super().DriverLaunch(
                            message="Webdriver encerrado inesperadamente, reinicializando..."
                        )

                    old_message = self.message

                    CrawJUD.auth_bot()

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

    def queue(self) -> None:

        try:
            search = self.SearchBot()
            self.bot_data = self.elawFormats(self.bot_data)

            if search is True:

                self.message = "Inicializando complemento de cadastro"
                self.type_log = "log"
                self.prt()
                edit_proc_button = self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, self.elements.botao_editar_complementar)
                    )
                )
                edit_proc_button.click()

                lista1 = list(self.bot_data.keys())

                start_time = time.perf_counter()

                check_esfera = self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, self.elements.label_esfera)
                    )
                )

                esfera_xls = self.bot_data.get("ESFERA")

                if esfera_xls:
                    if check_esfera.text.lower() != esfera_xls.lower():
                        complement.esfera(self, esfera_xls)

                for item in lista1:
                    check_column = self.bot_data.get(item.upper())

                    if check_column:
                        func: Callable[[], None] = getattr(
                            complement, item.lower(), None
                        )

                        if func:
                            func(self)

                end_time = time.perf_counter()
                execution_time = end_time - start_time
                calc = execution_time / 60
                splitcalc = str(calc).split(".")
                minutes = int(splitcalc[0])
                seconds = int(float(f"0.{splitcalc[1]}") * 60)

                self.validar_campos()

                self.validar_advs_participantes()

                self.salvar_tudo()

                if self.confirm_save() is True:
                    name_comprovante = self.print_comprovante()
                    self.message = "Processo salvo com sucesso!"

                self.append_success(
                    [
                        self.bot_data.get("NUMERO_PROCESSO"),
                        self.message,
                        name_comprovante,
                    ],
                    self.message,
                )
                self.message = (
                    f"Formulário preenchido em {minutes} minutos e {seconds} segundos"
                )

                self.type_log = "log"
                self.prt()

            elif search is not True:
                raise ErroDeExecucao("Processo não encontrado!")

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def salvar_tudo(self) -> None:

        self.interact.sleep_load('div[id="j_id_3x"]')
        salvartudo: WebElement = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.elements.css_salvar_proc)
            )
        )
        self.type_log = "log"
        self.message = "Salvando processo novo"
        self.prt()
        salvartudo.click()

    def validar_campos(self) -> None:

        self.message = "Validando campos"
        self.type_log = "log"
        self.prt()

        # message_campo: List[str] = []

        # for campo in campos_obrigatorios:
        #     try:

        #         campo_validar = self.elements.dict_campos_validar.get(campo)
        #         command = f"return $('{campo_validar}').text()"
        #         element = self.driver.execute_script(command)

        #         if not element or element.lower() == "selecione":
        #             raise ErroDeExecucao(message=f"Campo {campo} não preenchido")

        #         message_campo.append(
        #             f'<p class="fw-bold">Campo "{campo}" Validado | Texto: {element}</p>'
        #         )

        #     except Exception as e:
        #         raise ErroDeExecucao(e=e)

        # sleep(0.5)

        # message_campo.append('<p class="fw-bold">Campos obrigatórios validados!</p>')

        # self.message = "".join(message_campo)
        # self.type_log = "log"
        # self.prt()

        validar: Dict[str, str] = {
            "NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO")
        }
        message_campo: List[str] = []

        for campo in campos_validar:

            try:
                campo_validar: str = self.elements.dict_campos_validar.get(campo)
                command = f"return $('{campo_validar}').text()"
                element = self.driver.execute_script(command)

                if not element or element.lower() == "selecione":
                    raise ErroDeExecucao(message=f'Campo "{campo}" não preenchido')
                    # self.message = f'Campo "{campo}" não preenchido'
                    # self.type_log = "info"
                    # self.prt()

                message_campo.append(
                    f'<p class="fw-bold">Campo "{campo}" Validado | Texto: {element}</p>'
                )
                validar.update({campo.upper(): element})

            except Exception as e:

                try:
                    message = e.message

                except Exception as e:
                    message = str(e)

                validar.update({campo.upper(): message})

                self.message = message
                self.type_log = "info"
                self.prt()

        self.append_validarcampos([validar])
        message_campo.append('<p class="fw-bold">Campos validados!</p>')
        self.message = "".join(message_campo)
        self.type_log = "info"
        self.prt()

    def validar_advogado(self) -> str:

        self.message = "Validando advogado responsável"
        self.type_log = "log"
        self.prt()

        campo_validar = self.elements.dict_campos_validar.get("advogado_interno")
        command = f"return $('{campo_validar}').text()"
        element = self.driver.execute_script(command)

        if not element or element.lower() == "selecione":
            raise ErroDeExecucao(message='Campo "Advogado Responsável" não preenchido')

        self.message = f'Campo "Advogado Responsável" | Texto: {element}'
        self.type_log = "info"
        self.prt()

        sleep(0.5)

        return element

    def validar_advs_participantes(self) -> None:

        data_bot = self.bot_data
        adv_name = data_bot.get("ADVOGADO_INTERNO", self.validar_advogado())

        if not adv_name.strip():
            raise ErroDeExecucao(message="Necessário advogado interno para validação!")

        self.message = "Validando advogados participantes"
        self.type_log = "log"
        self.prt()

        tb_Advs = self.driver.find_element(By.CSS_SELECTOR, self.elements.tb_advs_resp)

        not_adv = None
        with suppress(NoSuchElementException):
            tr_not_adv = self.elements.tr_not_adv
            not_adv = tb_Advs.find_element(By.CSS_SELECTOR, tr_not_adv)

        if not_adv is not None:
            raise ErroDeExecucao(message="Sem advogados participantes!")

        advs = tb_Advs.find_elements(By.TAG_NAME, "tr")

        for adv in advs:
            advogado = adv.find_element(By.TAG_NAME, "td").text
            if advogado.lower() == adv_name.lower():
                break

        else:
            raise ErroDeExecucao(
                message="Advogado responsável não encontrado na lista de advogados participantes!"
            )

        self.message = "Advogados participantes validados"
        self.type_log = "info"
        self.prt()

    def confirm_save(self) -> bool:

        wait_confirm_save = None

        with suppress(TimeoutException):
            wait_confirm_save: WebElement = WebDriverWait(self.driver, 20).until(
                EC.url_to_be(("https://amazonas.elaw.com.br/processoView.elaw"))
            )

        if wait_confirm_save:
            return True

        elif not wait_confirm_save:
            ErroElaw: WebElement | str = None
            with suppress(TimeoutException, NoSuchElementException):
                ErroElaw = (
                    self.wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, self.elements.div_messageerro_css)
                        ),
                        message="Erro ao encontrar elemento",
                    )
                    .find_element(By.TAG_NAME, "ul")
                    .text
                )

            if not ErroElaw:
                ErroElaw = "Cadastro do processo nao finalizado, verificar manualmente"

            raise ErroDeExecucao(ErroElaw)

        # elif not wait_confirm_save:
        #     div_messageerro_css = 'div[id="messages"]'
        #     try:
        #         message: WebElement = self.wait.until(EC.presence_of_element_located(
        #             (By.CSS_SELECTOR, div_messageerro_css))).find_element(By.TAG_NAME, "ul").text

        #         raise ErroDeExecucao(self.message)

        #     except Exception as e:
        #         self.message = "Processo Não cadastrado"
        #         raise ErroDeExecucao(self.message)

    def print_comprovante(self) -> str:

        name_comprovante = f'Comprovante Cadastro - {self.bot_data.get("NUMERO_PROCESSO")} - PID {self.pid}.png'
        savecomprovante = os.path.join(
            pathlib.Path(__file__).cwd(), "exec", self.pid, name_comprovante
        )
        self.driver.get_screenshot_as_file(savecomprovante)
        return name_comprovante

    @classmethod
    def esfera(cls, self: Self, text: str = "Judicial") -> None:
        """
        Handles the selection of the judicial sphere in the process.
        This function performs the following steps:
        1. Selects the judicial sphere element.
        2. Sets the text to "Judicial".
        3. Logs the message "Informando esfera do processo".
        4. Calls the Select2_ELAW method to select the element.
        5. Waits for the loading of the specified div element.
        6. Logs the message "Esfera Informada!".
        Returns:
            None
        """

        elementSelect = self.elements.css_esfera_judge

        self.message = "Informando esfera do processo"
        self.type_log = "log"
        self.prt()

        self.Select2_ELAW(elementSelect, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Esfera Informada!"
        self.type_log = "info"
        self.prt()

    @classmethod
    def estado(cls, self: Self) -> None:
        """Declaração dos CSS em variáveis"""

        key = "ESTADO"
        elementSelect = self.elements.estado_input
        text = str(self.bot_data.get(key, None))

        self.message = "Informando estado do processo"
        self.type_log = "log"
        self.prt()

        self.Select2_ELAW(elementSelect, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Estado do processo informado!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def comarca(cls, self: Self) -> None:
        """Declaração dos CSS em variáveis"""

        text = str(self.bot_data.get("COMARCA"))
        elementSelect = self.elements.comarca_input

        self.message = "Informando comarca do processo"
        self.type_log = "log"
        self.prt()

        self.Select2_ELAW(elementSelect, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Comarca do processo informado!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def foro(cls, self: Self) -> None:
        """Declaração dos CSS em variáveis"""

        elementSelect = self.elements.foro_input
        text = str(self.bot_data.get("FORO"))

        self.message = "Informando foro do processo"
        self.type_log = "log"
        self.prt()

        self.Select2_ELAW(elementSelect, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Foro do processo informado!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def vara(cls, self: Self) -> None:
        """Declaração dos CSS em variáveis"""

        text = self.bot_data.get("VARA")
        elementSelect = self.elements.vara_input

        self.message = "Informando vara do processo"
        self.type_log = "log"
        self.prt()

        self.Select2_ELAW(elementSelect, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Vara do processo informado!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def unidade_consumidora(cls, self: Self) -> None:
        """
        Handles the process of informing the consumer unit in the web application.
        This function performs the following steps:
        1. Logs the start of the process.
        2. Waits for the input field for the consumer unit to be present in the DOM.
        3. Clicks on the input field.
        4. Clears any existing text in the input field.
        5. Sends the consumer unit data to the input field.
        6. Logs the completion of the process.
        Attributes:
            self.message (str): Message to be logged.
            self.type_log (str): Type of log to be recorded.
            self.elements.css_input_uc (str): CSS selector for the consumer unit input field.
            self.bot_data (dict): Dictionary containing the consumer unit data.
            self.prt(): Method to print/log messages.
            self.wait.until(): Method to wait until a condition is met.
            self.interact.clear(): Method to clear the input field.
            self.interact.send_key(): Method to send keys to the input field.
        """

        self.message = "Informando unidade consumidora"
        self.type_log = "log"
        self.prt()

        input_uc: WebElement = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.elements.css_input_uc)
            )
        )
        input_uc.click()

        self.interact.clear(input_uc)

        self.interact.send_key(input_uc, self.bot_data.get("UNIDADE_CONSUMIDORA"))

        self.message = "Unidade consumidora informada!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def divisao(cls, self: Self) -> None:

        self.message = "Informando divisão"
        self.type_log = "log"
        self.prt()

        sleep(0.5)
        text = str(self.bot_data.get("DIVISAO"))

        self.Select2_ELAW(self.elements.elementSelect, text)

        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Divisão informada!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def data_citacao(cls, self: Self) -> None:

        self.message = "Informando data de citação"
        self.type_log = "log"
        self.prt()

        data_citacao: WebElement = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.elements.css_data_citacao)
            )
        )
        self.interact.clear(data_citacao)
        self.interact.sleep_load('div[id="j_id_3x"]')
        self.interact.send_key(data_citacao, self.bot_data.get("DATA_CITACAO"))
        sleep(2)
        self.driver.execute_script(
            f"document.querySelector('{self.elements.css_data_citacao}').blur()"
        )
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Data de citação informada!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def fase(cls, self: Self) -> None:
        """Declaração dos CSS em variáveis"""
        elementSelect = self.elements.fase_input
        text = self.bot_data.get("FASE")

        self.message = "Informando fase do processo"
        self.type_log = "log"
        self.prt()

        self.Select2_ELAW(elementSelect, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Fase informada!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def provimento(cls, self: Self) -> None:
        """Declaração dos CSS em variáveis"""
        text = self.bot_data.get("PROVIMENTO")
        elementSelect = self.elements.provimento_input

        self.message = "Informando provimento antecipatório"
        self.type_log = "log"
        self.prt()

        self.Select2_ELAW(elementSelect, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Provimento antecipatório informado!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def valor_causa(cls, self: Self) -> None:
        """
        Fills in the value of the cause in a web form.
        This method performs the following steps:
        1. Logs the start of the process.
        2. Waits for the element representing the value of the cause to be clickable.
        3. Clicks on the element, clears any existing text, and inputs the new value.
        4. Executes a JavaScript command to remove focus from the input field.
        5. Waits for a specific loading element to disappear.
        6. Logs the completion of the process.
        Raises:
            TimeoutException: If the element is not found within the specified wait time.
        """

        self.message = "Informando valor da causa"
        self.type_log = "log"
        self.prt()

        valor_causa: WebElement = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, self.elements.css_valor_causa)
            ),
            message="Erro ao encontrar elemento",
        )

        valor_causa.click()
        sleep(0.5)
        valor_causa.clear()

        self.interact.send_key(valor_causa, self.bot_data.get("VALOR_CAUSA"))
        self.driver.execute_script(
            f"document.querySelector('{self.elements.css_valor_causa}').blur()"
        )

        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Valor da causa informado!"
        self.type_log = "info"
        self.prt()

    @classmethod
    def fato_gerador(cls, self: Self) -> None:
        """Declaração dos CSS em variáveis"""
        self.message = "Informando fato gerador"
        self.type_log = "log"
        self.prt()

        elementSelect = self.elements.fato_gerador_input
        text = self.bot_data.get("FATO_GERADOR")

        self.Select2_ELAW(elementSelect, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Fato gerador informado!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def desc_objeto(cls, self: Self) -> None:

        input_descobjeto = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.elements.input_descobjeto_css)
            )
        )
        self.interact.click(input_descobjeto)

        text = self.bot_data.get("DESC_OBJETO")

        self.interact.clear(input_descobjeto)
        self.interact.send_key(input_descobjeto, text)
        self.driver.execute_script(
            f"document.querySelector('{self.elements.input_descobjeto_css}').blur()"
        )
        self.interact.sleep_load('div[id="j_id_3x"]')

    @classmethod
    def objeto(cls, self: Self) -> None:
        """Declaração dos CSS em variáveis"""
        self.message = "Informando objeto do processo"
        self.type_log = "log"
        self.prt()

        elementSelect = self.elements.objeto_input
        text = self.bot_data.get("OBJETO")

        self.Select2_ELAW(elementSelect, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Objeto do processo informado!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def tipo_empresa(cls, self: Self) -> None:

        self.message = "Informando contingenciamento"
        self.type_log = "log"
        self.prt()

        elementSelect = self.elements.contingencia

        text = ["Passiva", "Passivo"]
        if str(self.bot_data.get("TIPO_EMPRESA")).lower() == "autor":
            text = ["Ativa", "Ativo"]

        self.Select2_ELAW(elementSelect, text[0])
        self.interact.sleep_load('div[id="j_id_3x"]')

        elementSelect = self.elements.tipo_polo

        text = ["Passiva", "Passivo"]
        if str(self.bot_data.get("TIPO_EMPRESA")).lower() == "autor":
            text = ["Ativa", "Ativo"]

        self.Select2_ELAW(elementSelect, text[1])
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Contingenciamento informado!"
        self.type_log = "info"
        self.prt()
