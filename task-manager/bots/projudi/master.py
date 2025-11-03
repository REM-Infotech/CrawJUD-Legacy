"""Módulo para a classe de controle dos robôs PROJUDI."""

from contextlib import suppress
from datetime import datetime
from time import sleep
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
from bs4.element import PageElement
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from bots.head import CrawJUD
from common.exceptions import (
    ExecutionError,
    LoginSystemError,
)
from constants import CSS_INPUT_PROCESSO
from resources.elements import projudi as el


class ProjudiBot(CrawJUD):
    """Classe de controle para robôs do PROJUDI."""

    url_segunda_instancia: str = None

    def search(self) -> bool:
        """Procura processos no PROJUDI.

        Returns:
            bool: True se encontrado; ou False
        redireciona pra cada rota apropriada

        """
        url_search = el.url_busca

        bot_data = self.bot_data
        driver = self.driver
        grau = int(bot_data.get("GRAU", 1) or 1)

        if grau == 2:
            if not self.url_segunda_instancia:
                self.url_segunda_instancia = driver.find_element(
                    By.CSS_SELECTOR,
                    'a[id="Stm0p7i1eHR"]',
                ).get_attribute("href")

            url_search = self.url_segunda_instancia

        driver.get(url_search)

        if self.botname != "proc_parte":
            return self.search_proc()

        return self.search_proc_parte()

    def search_proc(self) -> bool:
        """Pesquisa processo no PROJUDI.

        Returns:
            bool: True se encontrado; ou False
        manipula entradas, clique e tentativa condicional

        """
        bot_data = self.bot_data
        driver = self.driver

        numero_processo = bot_data["NUMERO_PROCESSO"]
        self.print_message(
            message=f"Buscando processo {numero_processo}",
            message_type="log",
        )

        grau = bot_data.get("GRAU", 1) or 1
        if isinstance(grau, str):
            grau = grau.strip()

        grau = int(grau)

        with suppress(TimeoutException):
            inputproc = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    CSS_INPUT_PROCESSO[str(grau)],
                )),
            )

            inputproc.send_keys(numero_processo)
            sleep(1)
            consultar = driver.find_element(By.CSS_SELECTOR, "#pesquisar")
            consultar.click()

            with suppress(TimeoutException, NoSuchElementException, Exception):
                WebDriverWait(driver, 5).until(
                    ec.presence_of_element_located((
                        By.XPATH,
                        '//*[@id="buscaProcessosQualquerInstanciaForm"]/table[2]/tbody/tr/td',
                    )),
                )

                with suppress(TimeoutException):
                    enterproc = WebDriverWait(driver, 5).until(
                        ec.presence_of_element_located((
                            By.CLASS_NAME,
                            "link",
                        )),
                    )

                    enterproc.click()
                    detect_intimacao(driver=driver)
                    allow_access(driver=driver)

                    self.print_message(
                        "Processo Encontrado!", message_type="info"
                    )

                    return True

        message_type = "error"
        message = "Processo não encontrado!"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        return False

    def search_proc_parte(self) -> bool:
        """Busca no PROJUDI nome da parte processual.

        Returns:
            bool: True se encontrado ou False.

        Insere dados, documento e gerencia pesquisa.

        """
        allprocess = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'input[value="qualquerAdvogado"]',
            )),
        )
        allprocess.click()
        data_inicio_xls = self.data_inicio
        data_fim_xls = self.data_fim

        if type(data_inicio_xls) is str:
            data_inicio_xls = datetime.strptime(
                data_inicio_xls,
                "%Y-%m-%d",
            ).replace(
                tzinfo=ZoneInfo("America/Manaus"),
            )
            data_inicio_xls = data_inicio_xls.strftime("%d/%m/%Y")

        if type(data_fim_xls) is str:
            data_fim_xls = datetime.strptime(data_fim_xls, "%Y-%m-%d").replace(
                tzinfo=ZoneInfo("America/Manaus"),
            )
            data_fim_xls = data_fim_xls.strftime("%d/%m/%Y")

        if self.vara == "TODAS AS COMARCAS":
            alljudge = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'input[name="pesquisarTodos"]',
                )),
            )
            alljudge.click()

        elif self.vara != "TODAS AS COMARCAS":
            search_vara = self.driver.find_element(By.ID, "descricaoVara")
            search_vara.click()
            search_vara.send_keys(self.vara)
            sleep(3)
            vara_option = self.driver.find_element(
                By.ID,
                "ajaxAuto_descricaoVara",
            ).find_elements(By.TAG_NAME, "li")[0]
            vara_option.click()

        sleep(3)
        input_parte = self.driver.find_element(
            By.CSS_SELECTOR,
            'input[name="nomeParte"]',
        )
        input_parte.send_keys(self.parte_name)

        cpfcnpj = self.driver.find_element(
            By.CSS_SELECTOR,
            'input[name="cpfCnpj"]',
        )
        cpfcnpj.send_keys(self.doc_parte)

        data_inicio = self.driver.find_element(
            By.CSS_SELECTOR,
            'input[id="dataInicio"]',
        )
        data_inicio.send_keys(data_inicio_xls)

        data_fim = self.driver.find_element(
            By.CSS_SELECTOR,
            'input[name="dataFim"]',
        )
        data_fim.send_keys(data_fim_xls)

        if self.polo_parte.lower() == "reu":
            set_reu = self.driver.find_element(
                By.CSS_SELECTOR,
                'input[value="promovido"]',
            )
            set_reu.click()

        elif self.polo_parte.lower() == "autor":
            setautor = self.driver.find_element(
                By.CSS_SELECTOR,
                'input[value="promovente"',
            )
            setautor.click()

        procenter = self.driver.find_element(By.ID, "pesquisar")
        procenter.click()
        sleep(3)

        with suppress(TimeoutException):
            enterproc = self.wait.until(
                ec.presence_of_element_located((By.CLASS_NAME, "link")),
            )

        return enterproc is not None

    def auth(self) -> bool:
        check_login = None
        try:
            self.driver.get(el.url_login)

            sleep(1.5)

            self.driver.refresh()

            username = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.campo_username,
                )),
            )
            username.send_keys(self.username)

            password = self.driver.find_element(
                By.CSS_SELECTOR,
                el.campo_2_login,
            )
            password.send_keys(self.password)

            entrar = self.driver.find_element(
                By.CSS_SELECTOR,
                el.btn_entrar,
            )
            entrar.click()

            with suppress(TimeoutException):
                check_login = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        el.chk_login,
                    )),
                )

            alert = None
            with suppress(TimeoutException, Exception):
                alert: type[Alert] = WebDriverWait(self.driver, 5).until(
                    ec.alert_is_present(),
                )

            if alert:
                alert.accept()

        except ExecutionError as e:
            raise LoginSystemError(exception=e) from e

        return check_login is not None

    def parse_data(self, inner_html: str) -> dict[str, str]:
        soup = BeautifulSoup(inner_html, "html.parser")
        dados = {}
        # percorre todas as linhas <tr>

        def normalize(txt: str) -> str:
            # Junta quebras de linha/tabs/múltiplos espaços em espaço simples
            return " ".join(txt.split())

        def get_text(td: PageElement) -> str:
            # Usa separador " " para não colar palavras; strip nas bordas
            return normalize(td.get_text(" ", strip=True))

        for tr in soup.find_all("tr"):
            tds = tr.find_all("td")
            i = 0
            while i < len(tds):
                td = tds[i]
                lbl_tag = td.find("label")
                if lbl_tag:
                    label = normalize(lbl_tag.get_text().rstrip(":"))
                    # avançar para o próximo td que tenha conteúdo real (pule espaçadores)
                    j = i + 1
                    valor = ""
                    while j < len(tds):
                        texto = get_text(tds[j])
                        # considera vazio se for "&nbsp;" ou string vazia
                        if texto and texto != " ":  # &nbsp; vira U+00A0
                            valor = texto
                            break
                        j += 1
                    if label and valor and ":" not in valor:
                        dados[label] = valor
                    # continue a partir do td seguinte ao que usamos como valor
                    i = j + 1
                else:
                    i += 1

        return dados


def detect_intimacao(driver: WebDriver) -> None:
    """Detecta intimação pendente de leitura no processo.

    Args:
        driver (WebDriver): Instância do navegador Selenium WebDriver.

    Raises:
        ExecutionError: Se houver intimação pendente de leitura.

    """
    if "intimacaoAdvogado.do" in driver.current_url:
        raise ExecutionError(
            message="Processo com Intimação pendente de leitura!",
        )


def allow_access(driver: WebDriver) -> None:
    """Permite acesso provisório ao processo no sistema PROJUDI.

    Args:
        driver (WebDriver): Instância do navegador Selenium WebDriver.

    Executa cliques para habilitar acesso provisório e aceitar termos.

    """
    with suppress(TimeoutException, NoSuchElementException):
        allowacess = driver.find_element(
            By.CSS_SELECTOR,
            "#habilitacaoProvisoriaButton",
        )

        allowacess.click()
        sleep(1)

        confirmterms = driver.find_element(
            By.CSS_SELECTOR,
            "#termoAceito",
        )
        confirmterms.click()
        sleep(1)

        save = driver.find_element(By.CSS_SELECTOR, "#saveButton")
        save.click()


def get_link_grau2(wait: WebDriverWait) -> str | None:
    """Recupera link para acessar processos em segundo grau.

    Filtra elemento com "Clique aqui para visualizar os recursos relacionados".

    Returns:
        str | None: link ou None.

    """
    with suppress(Exception, TimeoutException, NoSuchElementException):
        info_proc = wait.until(
            ec.presence_of_all_elements_located(
                (
                    By.CSS_SELECTOR,
                    "table#informacoesProcessuais > tbody > tr > td > a",
                ),
            ),
        )

        info_proc = list(
            filter(
                lambda x: "Clique aqui para visualizar os recursos relacionados"
                in x.text,
                info_proc,
            ),
        )[-1]

        return info_proc.get_attribute("href")
