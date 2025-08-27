"""Módulo para a classe de controle dos robôs PROJUDI."""

from __future__ import annotations

from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from crawjud.controllers.main import CrawJUD
from crawjud.resources.elements import csi as el

if TYPE_CHECKING:
    from crawjud.custom.task import ContextTask


workdir = Path(__file__).cwd()

HTTP_STATUS_FORBIDDEN = 403  # Constante para status HTTP Forbidden
COUNT_TRYS = 15
CSS_INPUT_PROCESSO = {
    "1": "#numeroProcesso",
    "2": "#numeroRecurso",
}


class CsiBot[T](CrawJUD):
    """Classe de controle para robôs do PROJUDI."""

    def __init__(
        self,
        current_task: ContextTask = None,
        storage_folder_name: str | None = None,
        name: str | None = None,
        system: str | None = None,
        *args: T,
        **kwargs: T,
    ) -> None:
        """Instancia a classe."""
        self.botname = name
        self.botsystem = system

        self.folder_storage = storage_folder_name
        self.current_task = current_task
        self.start_time = perf_counter()
        self.pid = str(current_task.request.id)

        super().__init__()

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
