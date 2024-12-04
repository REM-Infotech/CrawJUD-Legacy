""" calculadoras.tjdft """

import base64
import os
import time
from contextlib import suppress
from time import sleep

from selenium.common.exceptions import NoSuchWindowException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from urllib3.exceptions import MaxRetryError

from bot.common.exceptions import ErroDeExecucao
from bot.meta.CrawJUD import CrawJUD

cookieaceito = []


class tjdft(CrawJUD):

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
                message_error = str(e=e)

                self.type_log = "error"
                self.message_error = f"{message_error}. | Operação: {old_message}"
                self.prt()

                self.bot_data.update({"MOTIVO_ERRO": self.message_error})
                self.append_error(self.bot_data)

                self.message_error = None

        self.finalize_execution()

    def queue(self) -> None:

        self.get_calcular()
        self.info_numproc()
        self.info_requerente()
        self.info_requerido()
        self.info_jurosapartir()
        self.valores_devidos()
        self.acessorios()
        self.finalizar_execucao()

    def get_calcular(self) -> None:

        try:
            self.message = "Acessando Página de cálculo.."
            self.type_log = "log"
            self.prt()
            self.driver.get(
                "https://www.tjdft.jus.br/servicos/atualizacao-monetaria-1/calculo"
            )

            check_cookies = None
            with suppress(TimeoutException):
                check_cookies = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            'div[class="alert text-center cookiealert show"]',
                        )
                    )
                )

            if check_cookies:

                sleep(2)

                aceitar_cookies_css = (
                    'button[class="btn btn-primary btn-sm acceptcookies"]'
                )
                aceitar_cookies: WebElement = self.driver.find_element(
                    By.CSS_SELECTOR, aceitar_cookies_css
                )
                aceitar_cookies.click()
                self.driver.switch_to.default_content()

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def info_numproc(self) -> None:

        try:
            sleep(2)
            self.message = "Informando numero do processo"
            self.type_log = "log"
            self.prt()
            css_input_numproc = 'input[id="num_processo"][name="num_processo"]'
            get_input_process: WebElement = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_input_numproc))
            )
            get_input_process.click()
            get_input_process.send_keys(self.bot_data.get("NUMERO_PROCESSO"))

            self.message = "numero do processo informado"
            self.type_log = "log"
            self.prt()

        except Exception as e:
            raise ErroDeExecucao("Erro ao informar número do processo", e)

    def info_requerente(self) -> None:

        try:
            sleep(2)
            css_name_requerente = 'input[name="requerente"][id="requerente"]'
            self.message = "Informando requerente"
            self.type_log = "log"
            self.prt()
            get_name_requerente: WebElement = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_name_requerente))
            )
            get_name_requerente.click()
            get_name_requerente.send_keys(self.bot_data.get("REQUERENTE"))

            self.message = "Nome do requerente informado"
            self.type_log = "log"
            self.prt()

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def info_requerido(self) -> None:

        try:
            sleep(2)
            css_name_requerido = 'input[name="requerido"][id="requerido"]'
            self.message = "Informado requerido"
            self.type_log = "log"
            self.prt()
            get_name_requerido: WebElement = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_name_requerido))
            )
            get_name_requerido.click()
            get_name_requerido.send_keys(self.bot_data.get("REQUERIDO"))

            self.message = "Nome do requerido informado"
            self.type_log = "log"
            self.prt()

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def info_jurosapartir(self) -> None:

        try:
            self.message = "Informando incidencia de juros e data de incidencia"
            self.type_log = "log"
            self.prt()

            juros_partir = str(self.bot_data.get("JUROS_PARTIR")).upper()

            css_select_juros = 'select[id="juros_partir"][class="select-consultas"]'
            select = Select(
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, css_select_juros))
                )
            )
            select.select_by_value(juros_partir)

            juros_percent = str(self.bot_data.get("JUROS_PERCENT", "1"))
            if juros_percent == "1":
                self.interact.click(
                    self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="juros_percent1"]'
                    )
                )

            elif juros_percent != "1":

                percent = juros_percent
                percent = f"{percent},00" if "," not in percent else percent

                self.interact.click(
                    self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="juros_percent2"]'
                    )
                )
                self.interact.send_key(
                    self.wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'input[id="juros_percent_variavel"]')
                        )
                    ),
                    percent,
                )

            if not juros_partir == "VENCIMENTO":
                css_data_incide = 'input[name="juros_data"][id="juros_data"]'
                self.interact.send_key(
                    self.driver.find_element(By.CSS_SELECTOR, css_data_incide),
                    self.bot_data.get("DATA_INCIDENCIA"),
                )

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def valores_devidos(self) -> None:

        try:
            css_data_valor_devido = 'input[id="data-0"][name="parcela_data:list"]'
            self.message = "Informando data valor devido"
            self.type_log = "log"
            self.prt()
            data_valor_devido: WebElement = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_data_valor_devido))
            )
            data_valor_devido.click()
            data_valor_devido.send_keys(self.bot_data.get("DATA_CALCULO"))

            sleep(2)
            css_valor_devido = 'input[id="valor-0"][name="parcela_valor:list"]'
            self.message = "Informando valor devido"
            self.type_log = "log"
            self.prt()
            valor_devido: WebElement = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_valor_devido))
            )
            valor_devido.click()

            valor = str(self.bot_data.get("VALOR_CALCULO"))
            valor = f"{valor},00" if "," not in valor else valor
            valor_devido.send_keys(valor)

            self.message = "valor devido informado"
            self.type_log = "log"
            self.prt()

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def acessorios(self) -> None:

        def multa_percentual() -> None | Exception:

            try:
                sleep(1)
                css_multa_percentual = 'input[name="multa_percent"][id="multa_percent"]'
                self.message = "Informando multa percentual"
                self.type_log = "log"
                self.prt()

                if self.bot_data.get("MULTA_PERCENTUAL", None):
                    multa_percentual: WebElement = self.wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, css_multa_percentual)
                        )
                    )
                    multa_percentual.click()

                    percent = str(self.bot_data.get("MULTA_PERCENTUAL"))
                    percent = f"{percent},00" if "," not in percent else percent
                    multa_percentual.send_keys(percent)

                if self.bot_data.get("MULTA_DATA", None):

                    multa_data = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="multa_data"]'
                    )
                    multa_valor = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="multa_valor"]'
                    )

                    valor = str(self.bot_data.get("MULTA_VALOR"))
                    valor = f"{valor},00" if "," not in valor else valor

                    self.interact.send_key(multa_data, self.bot_data.get("MULTA_DATA"))
                    self.interact.send_key(multa_valor, valor)

                self.message = "Multa informada"
                self.type_log = "log"
                self.prt()

            except Exception as e:
                raise ErroDeExecucao(e=e)

        def honorario_sucumb() -> None | Exception:

            try:
                css_honorario_sucumb = (
                    'input[name="honor_sucumb_percent"][id="honor_sucumb_percent"]'
                )
                self.message = "Informando Honorários de Sucumbência"
                self.type_log = "log"
                self.prt()

                disabled_state = ""

                if self.bot_data.get("HONORARIO_SUCUMB_PERCENT", None):

                    honorario_sucumb: WebElement = self.wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, css_honorario_sucumb)
                        )
                    )
                    honorario_sucumb.click()
                    percent = str(self.bot_data.get("HONORARIO_SUCUMB_PERCENT"))
                    percent = f"{percent},00" if "," not in percent else percent

                    honorario_sucumb.send_keys(percent)
                    self.driver.execute_script(
                        f"document.querySelector('{css_honorario_sucumb}').blur()"
                    )
                    sleep(0.5)

                    disabled_state = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="honor_sucumb_data"]'
                    ).get_attribute("disabled")

                elif (
                    self.bot_data.get("HONORARIO_SUCUMB_DATA", None)
                    and disabled_state == ""
                ):

                    honor_sucumb_data = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="honor_sucumb_data"]'
                    )
                    honor_sucumb_valor = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="honor_sucumb_valor"]'
                    )
                    sucumb_juros_partir = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="honor_sucumb_juros_partir"]'
                    )

                    valor = str(self.bot_data.get("HONORARIO_SUCUMB_VALOR"))
                    valor = f"{valor},00" if "," not in valor else valor

                    self.interact.send_key(
                        honor_sucumb_data, self.bot_data.get("HONORARIO_SUCUMB_DATA")
                    )
                    self.interact.send_key(honor_sucumb_valor, valor)
                    self.interact.send_key(
                        sucumb_juros_partir,
                        self.bot_data.get("HONORARIO_SUCUMB_PARTIR"),
                    )

                self.message = "Percentual Honorários de Sucumbência informado"
                self.type_log = "log"
                self.prt()

            except Exception as e:
                raise ErroDeExecucao(e=e)

        def percent_multa_475J():

            try:
                percent_multa_ = self.driver.find_element(
                    By.CSS_SELECTOR, 'input[id="multa475_exec_percent"]'
                )
                self.interact.send_key(
                    percent_multa_, self.bot_data.get("PERCENT_MULTA_475J")
                )

            except Exception as e:
                raise ErroDeExecucao(e=e)

        def honorario_cumprimento() -> None | Exception:

            try:
                css_honorario_exec = 'input[id="honor_exec_percent"]'
                self.message = "Informando Honorários de Cumprimento"
                self.type_log = "log"
                self.prt()

                disabled_state = ""

                if self.bot_data.get("HONORARIO_CUMPRIMENTO_PERCENT", None):

                    honorario_exec: WebElement = self.wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, css_honorario_exec)
                        )
                    )
                    honorario_exec.click()
                    percent = str(self.bot_data.get("HONORARIO_CUMPRIMENTO_PERCENT"))
                    percent = f"{percent},00" if "," not in percent else percent

                    honorario_exec.send_keys(percent)
                    self.driver.execute_script(
                        f"document.querySelector('{css_honorario_exec}').blur()"
                    )
                    sleep(0.5)

                    disabled_state = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="honor_exec_data"]'
                    ).get_attribute("disabled")

                elif (
                    self.bot_data.get("HONORARIO_CUMPRIMENTO_DATA", None)
                    and disabled_state == ""
                ):

                    honor_exec_data = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="honor_exec_data"]'
                    )
                    honor_exec_valor = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="honor_exec_valor"]'
                    )
                    exec_juros_partir = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="honor_exec_juros_partir"]'
                    )

                    valor = str(self.bot_data.get("HONORARIO_CUMPRIMENTO_VALOR"))
                    valor = f"{valor},00" if "," not in valor else valor

                    self.interact.send_key(
                        honor_exec_data, self.bot_data.get("HONORARIO_CUMPRIMENTO_DATA")
                    )
                    self.interact.send_key(honor_exec_valor, valor)
                    self.interact.send_key(
                        exec_juros_partir,
                        self.bot_data.get("HONORARIO_CUMPRIMENTO_PARTIR"),
                    )

                self.message = "Informado Honorários de Cumprimento"
                self.type_log = "log"
                self.prt()

            except Exception as e:
                raise ErroDeExecucao(e=e)

        def custas() -> None | Exception:

            try:
                css_data_custas = 'input[id="custas-data-0"]'
                self.message = "Informando valor custas"
                self.type_log = "log"
                self.prt()
                data_custas: WebElement = self.driver.find_element(
                    By.CSS_SELECTOR, css_data_custas
                )
                data_custas.click()
                data_custas.send_keys(self.bot_data.get("CUSTAS_DATA"))

                sleep(2)
                css_custas_valor = 'input[id="custas-valor-0"]'
                self.message = "Informando valor devido"
                self.type_log = "log"
                self.prt()
                custas_valor: WebElement = self.driver.find_element(
                    By.CSS_SELECTOR, css_custas_valor
                )
                custas_valor.click()

                valor = str(self.bot_data.get("CUSTAS_VALOR"))
                valor = f"{valor},00" if "," not in valor else valor
                custas_valor.send_keys(valor)

                self.message = "Valor custas informado"
                self.type_log = "log"
                self.prt()

            except Exception as e:
                raise ErroDeExecucao(e=e)

        local_functions = list(locals().items())
        for name, func in local_functions:
            if not name == "self":
                for info in self.bot_data:
                    info = str(info)
                    if name.lower() in info.lower():
                        func()
                        break

    def finalizar_execucao(self) -> None:

        try:
            css_calcular = 'input[type="submit"][value="Calcular"][id="calcular"]'
            calcular = self.driver.find_element(By.CSS_SELECTOR, css_calcular)
            calcular.click()

            table_valorcalc: WebElement = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, 'table[class="grid listing"]')
                )
            )[-1]
            row_valorcalc = table_valorcalc.find_element(
                By.TAG_NAME, "tbody"
            ).find_elements(By.TAG_NAME, "tr")[-1]
            valor_doc = float(
                row_valorcalc.find_elements(By.TAG_NAME, "td")[-1]
                .text.replace(".", "")
                .replace(",", ".")
            )

            print_options = PrintOptions()
            print_options.orientation = "portrait"

            pdf = self.driver.print_page(print_options)
            pdf_bytes = base64.b64decode(pdf)

            # Salva o PDF em um arquivo

            pdf_name = f'CALCULO - {self.bot_data.get("NUMERO_PROCESSO")} - {self.bot_data.get("REQUERENTE")} - {self.pid}.pdf'

            path_pdf = os.path.join(self.output_dir_path, pdf_name)
            with open(path_pdf, "wb") as file:
                file.write(pdf_bytes)

            data = [self.bot_data.get("NUMERO_PROCESSO"), pdf_name, valor_doc]

            self.append_success(data)

        except Exception as e:
            raise ErroDeExecucao(e=e)
