from contextlib import suppress
from datetime import datetime
from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from ..common import ErroDeExecucao
from ..shared import PropertiesCrawJUD
from .PrintLogs import printbot


class SearchBot(PropertiesCrawJUD):

    prt = printbot.print_msg

    @classmethod
    def search_(cls) -> bool:

        cls.message = (
            f'Buscando processos pelo nome "{cls.parte_name}"'
            if cls.typebot == "proc_parte"
            else f'Buscando Processo Nº{cls.bot_data.get("NUMERO_PROCESSO")}'
        )
        cls.type_log = "log"
        cls.prt()

        src: bool = getattr(cls, f"{cls.system.lower()}_search", None)()

        if src is True:
            cls.message = "Processo encontrado!"
            cls.type_log = "log"
            cls.prt()

        return src

    @classmethod
    def elaw_search(cls) -> bool:

        if cls.driver.current_url != "https://amazonas.elaw.com.br/processoList.elaw":

            cls.driver.get("https://amazonas.elaw.com.br/processoList.elaw")

        campo_numproc: WebElement = cls.wait.until(
            EC.presence_of_element_located((By.ID, "tabSearchTab:txtSearch"))
        )
        campo_numproc.clear()
        sleep(0.15)
        cls.interact.send_key(campo_numproc, cls.bot_data.get("NUMERO_PROCESSO"))

        cls.driver.find_element(By.ID, "btnPesquisar").click()
        search_result: WebElement = cls.wait.until(
            EC.presence_of_element_located((By.ID, "dtProcessoResults_data"))
        )

        open_proc = None
        with suppress(NoSuchElementException):
            open_proc = search_result.find_element(
                By.ID, "dtProcessoResults:0:btnProcesso"
            )

        sleep(1.5)

        diff_cad = str(cls.typebot.upper()) != "CADASTRO"
        diff_complement = str(cls.typebot.upper()) != "COMPLEMENT"
        if open_proc:
            chkTypeBot = diff_cad and diff_complement
            if chkTypeBot:
                open_proc.click()

            return True

        return False

    @classmethod
    def esaj_search(cls) -> None:

        grau = cls.bot_data.get("GRAU", 1)

        if isinstance(grau, str):
            if "º" in grau:
                grau = grau.replace("º", "").replace(" ", "")

            grau = int(grau)

        if grau == 1:

            cls.driver.get(cls.elements.consultaproc_grau1)
            id_consultar = "botaoConsultarProcessos"

        elif grau == 2:

            cls.driver.get(cls.elements.consultaproc_grau2)
            id_consultar = "pbConsultar"

        elif not grau or grau != 1 or grau != 2:

            raise ErroDeExecucao("Informar instancia!")

        sleep(1)
        # Coloca o campo em formato "Outros" para inserir o número do processo
        ratioNumberOld: WebElement = cls.wait.until(
            EC.presence_of_element_located((By.ID, "radioNumeroAntigo"))
        )
        cls.interact.click(ratioNumberOld)

        # Insere o processo no Campo
        lineprocess: WebElement = cls.wait.until(
            EC.presence_of_element_located((By.ID, "nuProcessoAntigoFormatado"))
        )
        cls.interact.click(lineprocess)
        cls.interact.send_key(lineprocess, cls.bot_data.get("NUMERO_PROCESSO"))

        # Abre o Processo
        openprocess = None
        with suppress(TimeoutException):
            openprocess: WebElement = cls.wait.until(
                EC.presence_of_element_located((By.ID, id_consultar))
            )
            cls.interact.click(openprocess)

        check_process = None
        with suppress(NoSuchElementException, TimeoutException):
            check_process = WebDriverWait(cls.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#mensagemRetorno"))
            )

        # Retry 1
        if not check_process:
            with suppress(NoSuchElementException, TimeoutException):
                check_process: WebElement = WebDriverWait(cls.driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div[id="listagemDeProcessos"]')
                    )
                )

                if check_process:
                    check_process = (
                        check_process.find_element(By.TAG_NAME, "ul")
                        .find_elements(By.TAG_NAME, "li")[0]
                        .find_element(By.TAG_NAME, "a")
                    )

                    url_proc = check_process.get_attribute("href")
                    cls.driver.get(url_proc)

        # Retry 2
        if not check_process:
            with suppress(NoSuchElementException, TimeoutException):
                check_process: WebElement = WebDriverWait(cls.driver, 5).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            'div.modal__process-choice > input[type="radio"]',
                        )
                    )
                )

                if check_process:
                    check_process.click()
                    btEnviarIncidente = cls.driver.find_element(
                        By.CSS_SELECTOR, 'input[name="btEnviarIncidente"]'
                    )
                    btEnviarIncidente.click()

        return check_process is not None

    @classmethod
    def projudi_search(cls) -> None:

        cls.driver.get(cls.elements.url_busca)

        if cls.typebot != "proc_parte":

            returns = cls.search_proc()

        if cls.typebot == "proc_parte":
            returns = cls.search_proc_parte()

        return returns

    def search_proc(cls) -> bool:

        inputproc = None
        enterproc = None
        allowacess = None

        grau = int(str(cls.bot_data.get("GRAU", "1")).replace("º", ""))

        def detect_intimacao() -> None:

            if "intimacaoAdvogado.do" in cls.driver.current_url:
                raise ErroDeExecucao("Processo com Intimação pendente de leitura!")

        def get_link_grau2() -> str | None:
            with suppress(Exception, TimeoutException, NoSuchElementException):

                info_proc = cls.wait.until(
                    EC.presence_of_all_elements_located(
                        (
                            By.CSS_SELECTOR,
                            "table#informacoesProcessuais > tbody > tr > td > a",
                        )
                    )
                )

                info_proc = list(
                    filter(
                        lambda x: "Clique aqui para visualizar os recursos relacionados"
                        in x.text,
                        info_proc,
                    )
                )[-1]

                return info_proc.get_attribute("href")

            return None

        with suppress(TimeoutException):
            inputproc: WebElement = cls.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#numeroProcesso"))
            )

        if inputproc:
            inputproc.send_keys(cls.bot_data.get("NUMERO_PROCESSO"))
            consultar = cls.driver.find_element(By.CSS_SELECTOR, "#pesquisar")
            consultar.click()

            with suppress(TimeoutException):
                enterproc: WebElement = cls.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "link"))
                )

            if enterproc:

                enterproc.click()
                to_grau2 = get_link_grau2()

                detect_intimacao()

                with suppress(TimeoutException, NoSuchElementException):

                    allowacess = cls.driver.find_element(
                        By.CSS_SELECTOR, "#habilitacaoProvisoriaButton"
                    )

                if allowacess:
                    allowacess.click()
                    sleep(1)

                    confirmterms = cls.driver.find_element(
                        By.CSS_SELECTOR, "#termoAceito"
                    )
                    confirmterms.click()
                    sleep(1)

                    save = cls.driver.find_element(By.CSS_SELECTOR, "#saveButton")
                    save.click()

                if grau == 2 and to_grau2:
                    cls.driver.get(to_grau2)

                return True

            elif not enterproc:
                return False

        return False

    def search_proc_parte(cls) -> bool:

        allprocess = cls.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[value="qualquerAdvogado"]')
            )
        )
        allprocess.click()
        data_inicio_xls = cls.data_inicio
        data_fim_xls = cls.data_fim

        if type(data_inicio_xls) is str:
            data_inicio_xls = datetime.strptime(data_inicio_xls, "%Y-%m-%d")
            data_inicio_xls = data_inicio_xls.strftime("%d/%m/%Y")

        if type(data_fim_xls) is str:
            data_fim_xls = datetime.strptime(data_fim_xls, "%Y-%m-%d")
            data_fim_xls = data_fim_xls.strftime("%d/%m/%Y")

        if cls.vara == "TODAS AS COMARCAS":
            alljudge = WebDriverWait(cls.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[name="pesquisarTodos"]')
                )
            )
            alljudge.click()

        elif cls.vara != "TODAS AS COMARCAS":
            search_vara = cls.driver.find_element(By.ID, "descricaoVara")
            search_vara.click()
            search_vara.send_keys(cls.vara)
            sleep(3)
            vara_option = cls.driver.find_element(
                By.ID, "ajaxAuto_descricaoVara"
            ).find_elements(By.TAG_NAME, "li")[0]
            vara_option.click()

        sleep(3)
        input_parte = cls.driver.find_element(
            By.CSS_SELECTOR, 'input[name="nomeParte"]'
        )
        input_parte.send_keys(cls.parte_name)

        cpfcnpj = cls.driver.find_element(By.CSS_SELECTOR, 'input[name="cpfCnpj"]')
        cpfcnpj.send_keys(cls.doc_parte)

        data_inicio = cls.driver.find_element(By.CSS_SELECTOR, 'input[id="dataInicio"]')
        data_inicio.send_keys(data_inicio_xls)

        data_fim = cls.driver.find_element(By.CSS_SELECTOR, 'input[name="dataFim"]')
        data_fim.send_keys(data_fim_xls)

        if cls.polo_parte.lower() == "reu":
            setréu = cls.driver.find_element(
                By.CSS_SELECTOR, 'input[value="promovido"]'
            )
            setréu.click()

        elif cls.polo_parte.lower() == "autor":
            setautor = cls.driver.find_element(
                By.CSS_SELECTOR, 'input[value="promovente"'
            )
            setautor.click()

        procenter = cls.driver.find_element(By.ID, "pesquisar")
        procenter.click()
        sleep(3)

        with suppress(TimeoutException):
            enterproc: WebElement = cls.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "link"))
            )

        if enterproc:
            return True

        return False
