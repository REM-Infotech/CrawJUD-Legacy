import os
import time
import shutil
import pathlib
import unicodedata
from time import sleep
from contextlib import suppress


""" Imports do Projeto """
from bot.meta.CrawJUD import CrawJUD


from bot.common.exceptions import ErroDeExecucao


# Selenium Imports
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class protocolo(CrawJUD):

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

    def queue(self) -> None:

        self.SearchBot()
        self.init_protocolo()
        self.set_tipo_protocolo()
        self.set_subtipo_protocolo()
        self.set_petition_file()
        self.vincular_parte()
        self.finish_petition()
        data = self.get_confirm_protocol()
        self.append_success(data, message=data[1])

    def init_protocolo(self) -> None:

        try:
            try:
                self.prt.print_log(
                    "log", "Processo encontrado! Inicializando peticionamento..."
                )
                button_peticionamento: WebElement = WebDriverWait(
                    self.driver, 10
                ).until(EC.element_to_be_clickable((By.ID, "pbPeticionar")))
                link = button_peticionamento.get_attribute("onclick").split("'")[1]
                self.driver.execute_script(
                    "return window.location.href = '{link}';".format(link=link)
                )
                sleep(5)

            except Exception:

                button_enterproc: WebElement = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#processoSelecionado")
                    )
                )
                button_enterproc.click()

                enterproc: WebElement = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "#botaoEnviarIncidente")
                    )
                )
                enterproc.click()
                button_peticionamento: WebElement = WebDriverWait(
                    self.driver, 10
                ).until(EC.element_to_be_clickable((By.ID, "pbPeticionar")))
                link = button_peticionamento.get_attribute("onclick").split("'")[1]
                self.driver.execute_script(
                    "return window.location.href = '{link}';".format(link=link)
                )

        except Exception:
            raise ErroDeExecucao("Erro ao inicializar peticionamento")

    def set_tipo_protocolo(self) -> None:

        try:
            self.interact.sleep_load('div[id="loadFeedback"]')
            self.prt.print_log("log", "Informando tipo de peticionamento")
            button_classification: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.ID, self.elements.editar_classificacao)
                )
            )
            self.interact.click(button_classification)

            select_tipo_peticao: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.selecionar_classe)
                )
            )
            select_tipo_peticao = select_tipo_peticao.find_element(
                By.CSS_SELECTOR, self.elements.toggle
            )
            self.interact.click(select_tipo_peticao)

            input_tipo_peticao: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.input_classe)
                )
            )
            self.interact.send_key(
                input_tipo_peticao, self.bot_data.get("TIPO_PROTOCOLO")
            )
            sleep(1.5)
            self.interact.send_key(input_tipo_peticao, Keys.ENTER)

        except Exception:
            raise ErroDeExecucao("Erro ao informar tipo de protocolo")

    def set_subtipo_protocolo(self) -> None:

        try:
            self.prt.print_log("log", "Informando subtipo de peticionamento")
            select_categoria_peticao: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.select_categoria)
                )
            )
            select_categoria_peticao = select_categoria_peticao.find_element(
                By.CSS_SELECTOR, self.elements.toggle
            )
            self.interact.click(select_categoria_peticao)

            input_categoria_peticao: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.input_categoria)
                )
            )
            self.interact.send_key(
                input_categoria_peticao, self.bot_data.get("SUBTIPO_PROTOCOLO")
            )

            input_categoria_peticao_option: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, self.elements.selecionar_grupo)
                )
            )
            input_categoria_peticao_option.click()
            sleep(1)

        except Exception:
            raise ErroDeExecucao("Erro ao informar subtipo de protocolo")

    def set_petition_file(self) -> None:

        try:
            self.prt.print_log("log", "Anexando petição")
            input_file: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.input_documento)
                )
            )
            sleep(2)

            path_file = pathlib.Path(self.path_args).parent.resolve().__str__()
            file = os.path.join(path_file, self.bot_data.get("PETICAO_PRINCIPAL"))

            file = file.replace(" ", "")
            if "_" in file:
                file = file.replace("_", "")

            file = unicodedata.normalize("NFKD", file)
            file = "".join([c for c in file if not unicodedata.combining(c)])

            input_file.send_keys(file)

            file_uploaded = ""
            with suppress(TimeoutException):
                file_uploaded: WebElement = WebDriverWait(self.driver, 25).until(
                    EC.presence_of_element_located((By.XPATH, self.elements.documento))
                )

            if file_uploaded == "":
                raise ErroDeExecucao("Erro ao enviar petição")

            self.prt.print_log("log", "Petição do processo anexada com sucesso")

        except Exception:
            raise ErroDeExecucao("Erro ao enviar petição")

    def vincular_parte(self) -> None:

        try:
            parte_peticao = self.bot_data.get("PARTE_PETICIONANTE").__str__().lower()
            self.prt.print_log("log", "Vinculando parte a petição...")
            partes: WebElement = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, self.elements.processo_view)
                )
            )
            if partes:
                for parte in partes:
                    parte: WebElement = parte
                    parte_name = parte.find_element(
                        By.CSS_SELECTOR, self.elements.nome
                    ).text.lower()
                    if parte_name == parte_peticao:

                        sleep(3)

                        incluir_button = None
                        with suppress(NoSuchElementException):
                            incluir_button = parte.find_element(
                                By.CSS_SELECTOR, self.elements.botao_incluir_peticao
                            )

                        if not incluir_button:
                            with suppress(NoSuchElementException):
                                incluir_button = parte.find_element(
                                    By.CSS_SELECTOR,
                                    self.elements.botao_incluir_partecontraria,
                                )

                        incluir_button.click()

                        self.prt.print_log("log", "Vinculando cliente à petição...")
                        sleep(0.3)
                        break

                    if parte_name != parte_peticao:
                        partes = self.driver.find_elements(
                            By.CSS_SELECTOR, self.elements.parte_view
                        )
                        for parte in partes:
                            parte_name = parte.find_element(
                                By.CSS_SELECTOR, self.elements.nome
                            ).text.lower()
                            if parte_name == parte_peticao.lower():
                                self.prt.print_log(
                                    "log",
                                    "Parte já vinculada, finalizando peticionamento...",
                                )
                                sleep(0.3)
                                break

            elif not partes:
                raise ErroDeExecucao("Não foi possivel vincular parte a petição")

        except Exception:
            raise ErroDeExecucao("Não foi possivel vincular parte a petição")

    def finish_petition(self) -> None:

        self.prt.print_log("log", "Finalizando...")

        finish_button = self.driver.find_element(
            By.XPATH, self.elements.botao_protocolar
        )
        sleep(1)
        finish_button.click()
        sleep(5)

        confirm_button: WebElement = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.elements.botao_confirmar)
            )
        )
        confirm_button.click()

    def get_confirm_protocol(self) -> list:

        try:
            getlinkrecibo: WebElement = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.botao_recibo)
                )
            )

            sleep(3)

            name_recibo = f"Recibo Protocolo - {self.bot_data.get('NUMERO_PROCESSO')} - PID {self.pid}.pdf"
            self.driver.get_screenshot_as_file(
                f'{self.output_dir_path}/{name_recibo.replace(".pdf", ".png")}'
            )

            getlinkrecibo.click()

            path = os.path.join(self.output_dir_path, name_recibo)
            pathpdf = os.path.join(
                pathlib.Path(self.path_args).parent.resolve(), "recibo.pdf"
            )

            while True:

                if os.path.exists(pathpdf):
                    sleep(0.5)
                    break

            shutil.move(pathpdf, path)
            return [
                self.bot_data.get("NUMERO_PROCESSO"),
                f"Processo nº{self.bot_data.get('NUMERO_PROCESSO')} protocolado com sucesso!",
                name_recibo,
            ]

        except Exception as e:
            raise ErroDeExecucao("Erro ao confirmar protocolo", e=e)
