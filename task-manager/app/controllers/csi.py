"""Módulo para a classe de controle dos robôs PROJUDI."""

from __future__ import annotations

import platform
from contextlib import suppress
from pathlib import Path
from time import perf_counter, sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from app.common.exceptions.bot import raise_start_error
from app.controllers.main import CrawJUD
from app.resources.elements import csi as el

workdir = Path(__file__).cwd()


HTTP_STATUS_FORBIDDEN = 403  # Constante para status HTTP Forbidden
COUNT_TRYS = 15
CSS_INPUT_PROCESSO = {
    "1": "#numeroProcesso",
    "2": "#numeroRecurso",
}


class CsiBot(CrawJUD):
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

        selected_browser = "chrome"
        if platform.system() == "Linux":
            selected_browser = "firefox"

        super().__init__(selected_browser=selected_browser, *args, **kwargs)

        for k, v in kwargs.copy().items():
            setattr(self, k, v)

        self.download_files()

        self._frame = self.load_data()
        self.total_rows = len(self._frame)

        if not self.auth():
            self.error = self.total_rows

            self.print_msg(
                message="Falha na autenticação!",
                type_log="error",
            )

            with suppress(Exception):
                self.driver.quit()

            raise_start_error("Falha na autenticação.")

        self.print_msg(message="Sucesso na autenticação!", type_log="info")

        sleep(0.5)
        self.print_msg(message="Execução inicializada!", type_log="info")

    def search(self) -> bool:
        _url_search = el.url_busca

    def auth(self) -> bool:
        self.driver.get(el.URL_LOGIN)

        campo_username = self.wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_CAMPO_USERNAME,
            )),
        )
        campo_username.send_keys(self.username)

        campo_password = self.driver.find_element(
            By.XPATH,
            el.XPATH_CAMPO_SENHA,
        )
        campo_password.send_keys(self.password)

        btn_entrar = self.driver.find_element(
            By.XPATH,
            el.XPATH_BTN_ENTRAR,
        )
        btn_entrar.click()

        with suppress(Exception):
            self.wait.until(ec.url_to_be(el.URL_CONFIRMA_LOGIN))

            return True

        return False
