from time import sleep
from contextlib import suppress
from bot.common.exceptions import ErroDeExecucao

from datetime import datetime
from ..CrawJUD import CrawJUD
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException


class SeachBot(CrawJUD):

    def __init__(self):
        pass

    def __getattr__(self, nome):
        return super().__getattr__(nome)

    def __call__(self):

        self.message = (
            f'Buscando processos pelo nome "{self.parte_name}"'
            if self.typebot == "proc_parte"
            else f'Buscando Processo Nº{self.bot_data.get("NUMERO_PROCESSO")}'
        )
        self.type_log = "log"
        self.prt()

        src: bool = getattr(self, f"{self.system.lower()}_search", None)()

        if src is True:
            self.message = "Processo encontrado!"
            self.type_log = "info"
            self.prt()

        return src

    def elaw_search(self) -> bool:

        if self.driver.current_url != "https://amazonas.elaw.com.br/processoList.elaw":

            self.driver.get("https://amazonas.elaw.com.br/processoList.elaw")

        campo_numproc: WebElement = self.wait.until(
            EC.presence_of_element_located((By.ID, "tabSearchTab:txtSearch"))
        )
        campo_numproc.clear()
        sleep(0.15)
        self.interact.send_key(campo_numproc, self.bot_data.get("NUMERO_PROCESSO"))

        self.driver.find_element(By.ID, "btnPesquisar").click()
        search_result: WebElement = self.wait.until(
            EC.presence_of_element_located((By.ID, "dtProcessoResults_data"))
        )

        open_proc = None
        with suppress(NoSuchElementException):
            open_proc = search_result.find_element(
                By.ID, "dtProcessoResults:0:btnProcesso"
            )

        sleep(1.5)

        diff_cad = str(self.typebot.upper()) != "CADASTRO"
        diff_complement = str(self.typebot.upper()) != "COMPLEMENT"
        if open_proc:
            chkTypeBot = diff_cad and diff_complement
            if chkTypeBot:
                open_proc.click()

            return True

        return False

    def esaj_search(self) -> None:

        grau = int(self.bot_data.get("GRAU", "1").replace("º", ""))
        if grau == 1:

            self.driver.get(self.elements.consultaproc_grau1)
            id_consultar = "botaoConsultarProcessos"

        elif grau == 2:

            self.driver.get(self.elements.consultaproc_grau2)
            id_consultar = "pbConsultar"

        elif not grau or grau != 1 or grau != 2:

            raise ErroDeExecucao("Informar instancia!")

        sleep(1)
        # Coloca o campo em formato "Outros" para inserir o número do processo
        ratioNumberOld: WebElement = self.wait.until(
            EC.presence_of_element_located((By.ID, "radioNumeroAntigo"))
        )
        self.interact.click(ratioNumberOld)

        # Insere o processo no Campo
        lineprocess: WebElement = self.wait.until(
            EC.presence_of_element_located((By.ID, "nuProcessoAntigoFormatado"))
        )
        self.interact.click(lineprocess)
        self.interact.send_key(lineprocess, self.bot_data.get("NUMERO_PROCESSO"))

        # Abre o Processo
        openprocess = None
        with suppress(TimeoutException):
            openprocess: WebElement = self.wait.until(
                EC.presence_of_element_located((By.ID, id_consultar))
            )
            self.interact.click(openprocess)

        return openprocess is not None

    def projudi_search(self) -> None:

        def detect_intimacao() -> None:

            if "intimacaoAdvogado.do" in self.driver.current_url:
                raise ErroDeExecucao("Processo com Intimação pendente de leitura!")

        self.driver.get(self.elements.url_busca)

        inputproc = None
        enterproc = None
        allowacess = None

        if self.typebot != "proc_parte":

            with suppress(TimeoutException):
                inputproc: WebElement = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#numeroProcesso"))
                )

            if inputproc:
                inputproc.send_keys(self.bot_data.get("NUMERO_PROCESSO"))
                consultar = self.driver.find_element(By.CSS_SELECTOR, "#pesquisar")
                consultar.click()

                with suppress(TimeoutException):
                    enterproc: WebElement = self.wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, "link"))
                    )

                if enterproc:
                    enterproc.click()

                    detect_intimacao()

                    with suppress(TimeoutException, NoSuchElementException):

                        allowacess = self.driver.find_element(
                            By.CSS_SELECTOR, "#habilitacaoProvisoriaButton"
                        )

                    if allowacess:
                        allowacess.click()
                        sleep(1)

                        confirmterms = self.driver.find_element(
                            By.CSS_SELECTOR, "#termoAceito"
                        )
                        confirmterms.click()
                        sleep(1)

                        save = self.driver.find_element(By.CSS_SELECTOR, "#saveButton")
                        save.click()

                    return True

                elif not enterproc:
                    return False

        if self.typebot == "proc_parte":

            allprocess = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[value="qualquerAdvogado"]')
                )
            )
            allprocess.click()
            data_inicio_xls = self.data_inicio
            data_fim_xls = self.data_fim

            if type(data_inicio_xls) is str:
                data_inicio_xls = datetime.strptime(data_inicio_xls, "%Y-%m-%d")
                data_inicio_xls = data_inicio_xls.strftime("%d/%m/%Y")

            if type(data_fim_xls) is str:
                data_fim_xls = datetime.strptime(data_fim_xls, "%Y-%m-%d")
                data_fim_xls = data_fim_xls.strftime("%d/%m/%Y")

            if self.vara == "TODAS AS COMARCAS":
                alljudge = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'input[name="pesquisarTodos"]')
                    )
                )
                alljudge.click()

            elif self.vara != "TODAS AS COMARCAS":
                search_vara = self.driver.find_element(By.ID, "descricaoVara")
                search_vara.click()
                search_vara.send_keys(self.vara)
                sleep(3)
                vara_option = self.driver.find_element(
                    By.ID, "ajaxAuto_descricaoVara"
                ).find_elements(By.TAG_NAME, "li")[0]
                vara_option.click()

            sleep(3)
            input_parte = self.driver.find_element(
                By.CSS_SELECTOR, 'input[name="nomeParte"]'
            )
            input_parte.send_keys(self.parte_name)

            cpfcnpj = self.driver.find_element(By.CSS_SELECTOR, 'input[name="cpfCnpj"]')
            cpfcnpj.send_keys(self.doc_parte)

            data_inicio = self.driver.find_element(
                By.CSS_SELECTOR, 'input[id="dataInicio"]'
            )
            data_inicio.send_keys(data_inicio_xls)

            data_fim = self.driver.find_element(
                By.CSS_SELECTOR, 'input[name="dataFim"]'
            )
            data_fim.send_keys(data_fim_xls)

            if self.polo_parte.lower() == "reu":
                setréu = self.driver.find_element(
                    By.CSS_SELECTOR, 'input[value="promovido"]'
                )
                setréu.click()

            elif self.polo_parte.lower() == "autor":
                setautor = self.driver.find_element(
                    By.CSS_SELECTOR, 'input[value="promovente"'
                )
                setautor.click()

            procenter = self.driver.find_element(By.ID, "pesquisar")
            procenter.click()
            sleep(3)

            with suppress(TimeoutException):
                enterproc: WebElement = self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "link"))
                )

            if enterproc:
                return True

            return False
