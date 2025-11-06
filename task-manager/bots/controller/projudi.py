"""Módulo para a classe de controle dos robôs PROJUDI."""

from contextlib import suppress
from datetime import datetime
from time import sleep
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from bots.head import CrawJUD
from bots.resources.elements import projudi as el
from bots.resources.formatadores import formata_string
from common.exceptions import (
    ExecutionError,
    LoginSystemError,
)
from constants import CSS_INPUT_PROCESSO, MAIOR_60_ANOS, VER_RECURSO

if TYPE_CHECKING:
    from bs4._typing import _SomeTags
    from selenium.webdriver.common.alert import Alert
    from selenium.webdriver.remote.webdriver import WebDriver


class ProjudiBot(CrawJUD):
    """Classe de controle para robôs do PROJUDI."""

    url_segunda_instancia: str = None
    rows_data: _SomeTags

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

        if self.config.get("categoria") != "proc_parte":
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
            consultar = driver.find_element(
                By.CSS_SELECTOR,
                "#pesquisar",
            )
            consultar.click()

            with suppress(
                TimeoutException,
                NoSuchElementException,
                Exception,
            ):
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
                        "Processo Encontrado!",
                        message_type="info",
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
            data_fim_xls = datetime.strptime(
                data_fim_xls,
                "%Y-%m-%d",
            ).replace(
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
            search_vara = self.driver.find_element(
                By.ID,
                "descricaoVara",
            )
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
        """Autentique usuário no sistema PROJUDI.

        Returns:
            bool: True se login bem-sucedido, False caso contrário.

        Raises:
            LoginSystemError: Se ocorrer erro na autenticação.

        """
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
            username.send_keys(self.credenciais.username)

            password = self.driver.find_element(
                By.CSS_SELECTOR,
                el.campo_2_login,
            )
            password.send_keys(self.credenciais.password)

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
                alert: type[Alert] = WebDriverWait(
                    self.driver,
                    5,
                ).until(
                    ec.alert_is_present(),
                )

            if alert:
                alert.accept()

        except ExecutionError as e:
            raise LoginSystemError(exception=e) from e

        return check_login is not None

    def parse_data(self, inner_html: str) -> dict[str, str]:
        """Extrai dados do HTML do processo.

        Args:
            inner_html (str): HTML da página do processo.

        Returns:
            dict[str, str]: Dados extraídos do processo.

        """
        soup = BeautifulSoup(inner_html, "html.parser")
        dados = {}
        # percorre todas as linhas <tr>

        self.rows_data = []
        for table_row in soup.find_all("tr"):
            table_row_data = table_row.find_all("td")
            self.rows_data.extend(table_row_data)

        for pos, td in enumerate(self.rows_data):
            lbl_tag = td.find("label")
            if lbl_tag:
                label = self.__normalize(lbl_tag.get_text().rstrip(":"))
                valor = self.__get_text(pos)

                if self.__value_check(label, valor):
                    dados[formata_string(label)] = valor

        return dados

    def __value_check(self, label: str, valor: str) -> bool:
        if label and valor and ":" not in valor:
            return valor != MAIOR_60_ANOS and valor != VER_RECURSO

        return False

    def __get_text(self, pos: int) -> str:
        i = pos + 1
        while i < len(self.rows_data):
            valor = self.__normalize(
                self.rows_data[i].get_text(" ", strip=True),
            )
            if valor and valor != " ":
                return valor
            i += 1
        return None

    def __normalize(self, txt: str) -> str:
        return " ".join(txt.split())


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
    """Retorne link de recursos do grau 2 do processo.

    Args:
        wait (WebDriverWait): Espera explícita do Selenium.

    Returns:
        str | None: Link encontrado ou None.

    """
    with suppress(Exception, TimeoutException, NoSuchElementException):
        btn_txt = "Clique aqui para visualizar os recursos relacionados"
        info_proc = wait.until(
            ec.presence_of_all_elements_located(
                (
                    By.CSS_SELECTOR,
                    el.INFORMACAO_PROCESSO,
                ),
            ),
        )

        info_proc = list(
            filter(
                lambda x: btn_txt in x.text,
                info_proc,
            ),
        )[-1]

        return info_proc.get_attribute("href")
