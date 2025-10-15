"""Módulo para a classe de controle dos robôs CAIXA."""

from __future__ import annotations

import platform
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from time import perf_counter, sleep
from typing import TYPE_CHECKING

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from app.controllers.main import CrawJUD

if TYPE_CHECKING:
    from app.custom.task import ContextTask
    from app.interfaces.types import T

DictData = dict[str, str | datetime]
ListData = list[DictData]

workdir = Path(__file__).cwd()

HTTP_STATUS_FORBIDDEN = 403  # Constante para status HTTP Forbidden
COUNT_TRYS = 15
CSS_INPUT_PROCESSO = {
    "1": "#numeroProcesso",
    "2": "#numeroRecurso",
}


class CaixaBot(CrawJUD):
    """Classe de controle para robôs do Caixa."""

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

        sleep(0.5)
        self.print_msg(message="Execução inicializada!", type_log="info")

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
