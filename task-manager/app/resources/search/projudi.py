from contextlib import suppress
from time import sleep
from typing import TYPE_CHECKING

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from app.common.exceptions import ExecutionError
from app.resources.elements import projudi as el
from app.resources.search._main import SearchBot
from constants import CSS_INPUT_PROCESSO

if TYPE_CHECKING:
    from app.controllers.projudi import ProjudiBot
    from app.interfaces import BotData
    from app.resources.driver.web_element import WebElementBot


GRAU_PRIMEIRA_INSTANCIA = 1
GRAU_SEGUNDA_INSTANCIA = 2


class ProjudiSearch(SearchBot):
    bot: ProjudiBot
    bot_data: BotData

    def __call__(self) -> bool:
        """Procura processos no PROJUDI.

        Returns:
            bool: True se encontrado; ou False
        redireciona pra cada rota apropriada

        """
        url_search = el.url_busca
        grau = int(self.bot_data.get("GRAU", 1) or 1)

        if grau == GRAU_SEGUNDA_INSTANCIA:
            if not self.url_segunda_instancia:
                self.url_segunda_instancia = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'a[id="Stm0p7i1eHR"]',
                ).get_attribute("href")

            url_search = self.url_segunda_instancia

        self.driver.get(url_search)

        return self.search_proc()

    def search_proc(self) -> bool:
        """Pesquisa processo no PROJUDI.

        Returns:
            bool: True se encontrado; ou False
        manipula entradas, clique e tentativa condicional

        """
        bot_data = self.bot_data

        numero_processo = bot_data["NUMERO_PROCESSO"]
        self.print_message(
            message=f"Buscando processo n.{numero_processo}",
            message_type="log",
        )

        grau = bot_data.get("GRAU", 1) or 1
        if isinstance(grau, str):
            grau = grau.strip()

        grau = int(grau)

        self.__consultar_processo(
            numero_processo=numero_processo,
            grau=grau,
        )

        if self._verifica_processo_encontrado():
            return self.__acessar_processo()

        message_type = "error"
        message = "Processo não encontrado!"
        self.print_message(
            message=message,
            message_type=message_type,
        )

        return False

    def __consultar_processo(self, numero_processo: str, grau: int) -> None:
        with suppress(TimeoutException):
            inputproc = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    CSS_INPUT_PROCESSO[str(grau)],
                )),
            )

            inputproc.send_keys(numero_processo)
            sleep(1)
            consultar = self.driver.find_element(
                By.CSS_SELECTOR,
                "#pesquisar",
            )
            consultar.click()

    def _verifica_processo_encontrado(self) -> WebElementBot | None:
        with suppress(
            TimeoutException,
            NoSuchElementException,
            Exception,
        ):
            return WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located((
                    By.XPATH,
                    '//*[@id="buscaProcessosQualquerInstanciaForm"]/table[2]/tbody/tr/td',
                )),
            )

        return None

    def __acessar_processo(self) -> None:
        with suppress(TimeoutException):
            enterproc = WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located((
                    By.CLASS_NAME,
                    "link",
                )),
            )

            enterproc.click()
            self.detect_intimacao()
            self.allow_access()

            self.print_message(
                "Processo Encontrado!",
                message_type="info",
            )

            return True

    def detect_intimacao(self) -> None:
        """Detecta intimação pendente de leitura no processo.

        Args:
            driver (WebDriver): Instância do navegador Selenium WebDriver.

        Raises:
            ExecutionError: Se houver intimação pendente de leitura.

        """
        if "intimacaoAdvogado.do" in self.driver.current_url:
            raise ExecutionError(
                message="Processo com Intimação pendente de leitura!",
            )

    def allow_access(self) -> None:
        """Permite acesso provisório ao processo no sistema PROJUDI.

        Args:
            driver (WebDriver): Instância do navegador Selenium WebDriver.

        Executa cliques para habilitar acesso provisório e aceitar termos.

        """
        with suppress(TimeoutException, NoSuchElementException):
            allowacess = self.driver.find_element(
                By.CSS_SELECTOR,
                "#habilitacaoProvisoriaButton",
            )

            allowacess.click()
            sleep(1)

            confirmterms = self.driver.find_element(
                By.CSS_SELECTOR,
                "#termoAceito",
            )
            confirmterms.click()
            sleep(1)

            save = self.driver.find_element(By.CSS_SELECTOR, "#saveButton")
            save.click()

    def get_link_grau2(self) -> str | None:
        """Retorne link de recursos do grau 2 do processo.

        Args:
            wait (WebDriverWait): Espera explícita do Selenium.

        Returns:
            str | None: Link encontrado ou None.

        """
        with suppress(Exception, TimeoutException, NoSuchElementException):
            btn_txt = "Clique aqui para visualizar os recursos relacionados"
            info_proc = self.wait.until(
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
