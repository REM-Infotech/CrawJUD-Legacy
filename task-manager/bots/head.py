"""Abstração CrawJUD."""

from __future__ import annotations

from abc import abstractmethod
from contextlib import suppress
from threading import Event
from typing import ClassVar

from celery import shared_task
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome

import _hook
from __types import Dict
from bots.resources.driver import BotDriver
from bots.resources.managers.credencial_manager import CredencialManager
from bots.resources.managers.file_manager import FileManager
from bots.resources.queues.file_operation import SaveError, SaveSuccess
from bots.resources.queues.print_message import PrintMessage

__all__ = ["_hook"]


class CrawJUD:
    """Classe CrawJUD."""

    bots: ClassVar[Dict] = {}

    @property
    def driver(self) -> WebDriver | Chrome:
        return self.bot_driver.driver

    @property
    def wait(self) -> WebDriverWait[WebDriver | Chrome]:
        return self.bot_driver.wait

    def __init__(self) -> None:
        """Inicializa o CrawJUD."""

    def __init_subclass__(cls) -> None:
        module_split = cls.__module__.split(".")
        if (
            "master" in module_split
            or "controller" in module_split
            or len(set(module_split)) != len(module_split)
        ):
            return

        name_bot = "_".join(
            module_split[1:] if len(module_split) == 3 else module_split[2:]
        )
        if "__" in name_bot:
            return

        CrawJUD.bots[name_bot] = cls

    def setup(self, config: Dict) -> None:
        self.bot_stopped = Event()
        self.print_message = PrintMessage(self)
        self.append_succes = SaveSuccess(self)
        self.append_error = SaveError(self)
        self.credenciais = CredencialManager(self)
        self.file_manager = FileManager(self)

        self.file_manager.download_files()
        self.credenciais.load_credenciais(config)

        self.bot_driver = BotDriver(self)

        if not self.auth():
            with suppress(Exception):
                self.driver.quit()

        return self._task()

    def finalize_execution(self) -> None:
        with suppress(Exception):
            window_handles = self.driver.window_handles
            if window_handles:
                self.driver.delete_all_cookies()
                self.driver.quit()

        message = "Fim da execução"
        self.print_message(message=message, message_type="success")

        zip_file = self.zip_result()
        link = self.upload_file(zipfile=zip_file)

        message = f"Baixe os resultados aqui: {link}"
        self.print_message(message=message, message_type="info")

        self.queue_control.stop_queues()

    @abstractmethod
    def auth(self) -> bool:
        """Autenticação no sistema."""
        ...

    @abstractmethod
    def execution(self) -> None: ...


@shared_task(name="crawjud")
def start_bot(config: Dict) -> None:
    return CrawJUD().setup(config=config)
