""" Crawler ELAW Andamentos"""

import time
from contextlib import suppress
from time import sleep

from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib3.exceptions import MaxRetryError

from bot.common.exceptions import ErroDeExecucao
from bot.meta.CrawJUD import CrawJUD


class andamentos(CrawJUD):

    def __init__(self, **kwrgs) -> None:
        super().__init__(**kwrgs)
        super().setup()
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

    def queue(self) -> None:

        search = self.SearchBot()
        if search is True:
            btn_newmove = self.elements.botao_andamento
            new_move: WebElement = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, btn_newmove))
            )
            new_move.click()

            self.info_data()
            self.info_ocorrencia()
            self.info_observacao()

            if self.bot_data.get("ANEXOS", None):
                self.add_anexo()

            self.save_andamento()

        elif search is not True:
            self.message = "Processo não encontrado!"
            self.type_log = "error"
            self.prt()
            self.append_error([self.bot_data.get("NUMERO_PROCESSO"), self.message])

    def info_data(self) -> None:

        try:

            self.message = "Informando data"
            self.type_log = "log"
            self.prt()
            css_Data = self.elements.input_data
            campo_data: WebElement = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_Data))
            )
            campo_data.click()
            campo_data.send_keys(Keys.CONTROL, "a")
            sleep(0.5)
            campo_data.send_keys(Keys.BACKSPACE)
            self.interact.send_key(campo_data, self.bot_data.get("DATA"))
            campo_data.send_keys(Keys.TAB)

            self.interact.sleep_load('div[id="j_id_34"]')

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def info_ocorrencia(self) -> None:

        try:
            self.message = "Informando ocorrência"
            self.type_log = "log"
            self.prt()

            ocorrencia = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.inpt_ocorrencia
            )
            text_andamento = (
                str(self.bot_data.get("OCORRENCIA")).replace("\t", "").replace("\n", "")
            )

            self.interact.send_key(ocorrencia, text_andamento)

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def info_observacao(self) -> None:

        try:
            self.message = "Informando observação"
            self.type_log = "log"
            self.prt()

            observacao = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.inpt_obs
            )
            text_andamento = (
                str(self.bot_data.get("OBSERVACAO")).replace("\t", "").replace("\n", "")
            )

            self.interact.send_key(observacao, text_andamento)

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def add_anexo(self) -> None:

        pass

    def save_andamento(self) -> None:

        try:
            self.message = "Salvando andamento..."
            self.type_log = "log"
            self.prt()
            sleep(1)
            self.link = self.driver.current_url
            save_button = self.driver.find_element(
                By.ID, self.elements.botao_salvar_andamento
            )
            save_button.click()

        except Exception as e:
            raise ErroDeExecucao("Não foi possivel salvar andamento", e=e)

        try:
            check_save: WebElement = WebDriverWait(self.driver, 10).until(
                EC.url_to_be("https://amazonas.elaw.com.br/processoView.elaw")
            )
            if check_save:
                sleep(3)

                self.append_success(
                    [self.numproc, "Andamento salvo com sucesso!", ""],
                    "Andamento salvo com sucesso!",
                )

        except Exception:
            raise ErroDeExecucao(
                "Aviso: não foi possivel validar salvamento de andamento"
            )
