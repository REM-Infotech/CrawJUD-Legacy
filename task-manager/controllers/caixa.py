"""Módulo para a classe de controle dos robôs CAIXA."""

from contextlib import suppress
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from controllers._master import CrawJUD

DictData = dict[str, str | datetime]
ListData = list[DictData]


HTTP_STATUS_FORBIDDEN = 403  # Constante para status HTTP Forbidden
COUNT_TRYS = 15
CSS_INPUT_PROCESSO = {
    "1": "#numeroProcesso",
    "2": "#numeroRecurso",
}


class CaixaBot(CrawJUD):
    """Classe de controle para robôs do Caixa."""

    def wait_caixa(self) -> None:
        """Wait until a modal dialog (caixa) is displayed on the page."""
        while True:
            check_wait = None
            with suppress(NoSuchElementException):
                check_wait = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'div[id="modal:waitContainer"][style="position: absolute; z-index: 100; background-color: inherit; display: none;"]',
                )

            if check_wait:
                break
