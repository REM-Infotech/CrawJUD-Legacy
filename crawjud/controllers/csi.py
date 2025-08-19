"""Módulo para a classe de controle dos robôs PROJUDI."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from time import sleep  # noqa: F401
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo  # noqa: F401

from selenium.common.exceptions import (  # noqa: F401
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait  # noqa: F401

from crawjud.common.exceptions.bot import (  # noqa: F401
    ExecutionError,
    LoginSystemError,
)
from crawjud.controllers.master import CrawJUD
from crawjud.resources.elements import csi as el

if TYPE_CHECKING:
    from selenium.webdriver.common.alert import Alert  # noqa: F401
    from selenium.webdriver.remote.webdriver import WebDriver  # noqa: F401


DictData = dict[str, str | datetime]
ListData = list[DictData]

workdir = Path(__file__).cwd()

HTTP_STATUS_FORBIDDEN = 403  # Constante para status HTTP Forbidden
COUNT_TRYS = 15
CSS_INPUT_PROCESSO = {
    "1": "#numeroProcesso",
    "2": "#numeroRecurso",
}


class CsiBot[T](CrawJUD):
    """Classe de controle para robôs do PROJUDI."""

    def __init__(self, *args: T, **kwargs: T) -> None:
        """Instancia a classe."""
        super().__init__()

        self.folder_storage = kwargs.pop("storage_folder_name")

        for k, v in kwargs.copy().items():
            setattr(self, k, v)

        self.download_files()

        self.auth()
        self._frame = self.load_data()

    def search(self) -> bool:
        _url_search = el.url_busca

    def auth(self) -> bool:
        self.driver.get(el.url_login)

        campo_username = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.campo_username,
            )),
        )
        campo_username.send_keys(self.username)

        campo_password = self.driver.find_element(
            By.CSS_SELECTOR,
            el.campo_passkey,
        )
        campo_password.send_keys(self.password)

        btn_entrar = self.driver.find_element(By.CSS_SELECTOR, el.btn_entrar)
        btn_entrar.click()

        return self.wait.until(ec.url_to_be(el.url_logado))
