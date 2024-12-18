import os
import pathlib
import time
from contextlib import suppress
from time import sleep

from selenium.common.exceptions import (
    NoSuchElementException,
    NoSuchWindowException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib3.exceptions import MaxRetryError

from bot.common.exceptions import ErroDeExecucao
from bot.meta.CrawJUD import CrawJUD

type_doc = {11: "cpf", 14: "cnpj"}


class complement(CrawJUD):

    def __init__(self, **kwrgs):
        super().__init__(**kwrgs)
        super().setup()
        super().auth_bot()

        from clear import clear

        clear()
        print(self.__dict__.items())

        self.start_time = time.perf_counter()

    def execution(self):

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

                old_message = None
                check_window = any(
                    [isinstance(e, NoSuchWindowException), isinstance(e, MaxRetryError)]
                )
                if check_window:

                    with suppress(Exception):
                        super().DriverLaunch(
                            message="Webdriver encerrado inesperadamente, reinicializando..."
                        )

                        old_message = self.message

                        super().auth_bot()

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

    def queue(self):

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

            def esfera():

                elementSelect = self.elements.css_esfera_judge
                text = "Judicial"

                self.message = "Informando esfera do processo"
                self.type_log = "log"
                self.prt()

                self.Select2_ELAW(elementSelect, text)
                self.interact.sleep_load('div[id="j_id_3x"]')

                self.message = "Esfera Informada!"
                self.type_log = "info"
                self.prt()

            def unidade_consumidora():

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

                self.interact.send_key(
                    input_uc, self.bot_data.get("UNIDADE_CONSUMIDORA")
                )

                self.message = "Unidade consumidora informada!"
                self.type_log = "log"
                self.prt()

            def divisao():

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

            def data_citacao():

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

            def estado():
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

            def comarca():
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

            def foro():
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

            def vara():
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

            def fase():
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

            def provimento():
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

            def fato_gerador():
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

            def desc_objeto():

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

            def objeto():
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

            def tipo_empresa():

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

            start_time = time.perf_counter()
            class_itens = list(locals().items())

            check_esfera = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.label_esfera)
                )
            )

            if check_esfera.text == "Selecione":
                esfera()

            for item in lista1:
                check_column = self.bot_data.get(item.upper())

                if check_column:
                    func = None

                    for name, func in class_itens:
                        if name.lower() == item.lower():
                            func()
                            break

            end_time = time.perf_counter()
            execution_time = end_time - start_time
            calc = execution_time / 60
            splitcalc = str(calc).split(".")
            minutes = int(splitcalc[0])
            seconds = int(float(f"0.{splitcalc[1]}") * 60)

            self.message = (
                f"Formulário preenchido em {minutes} minutos e {seconds} segundos"
            )
            self.type_log = "log"
            self.prt()

            self.salvar_tudo()

            if self.confirm_save() is True:
                name_comprovante = self.print_comprovante()
                self.message = "Processo salvo com sucesso!"

            self.append_success(
                [self.bot_data.get("NUMERO_PROCESSO"), self.message, name_comprovante],
                self.message,
            )

        elif search is not True:
            raise ErroDeExecucao("Processo não encontrado!")

    def salvar_tudo(self):

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

    def print_comprovante(self) -> str:

        name_comprovante = f'Comprovante Cadastro - {self.bot_data.get("NUMERO_PROCESSO")} - PID {self.pid}.png'
        savecomprovante = os.path.join(
            pathlib.Path(__file__).cwd(), "exec", self.pid, name_comprovante
        )
        self.driver.get_screenshot_as_file(savecomprovante)
        return name_comprovante

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
