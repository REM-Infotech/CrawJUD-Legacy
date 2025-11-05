"""Abstração CrawJUD."""

from __future__ import annotations

from abc import abstractmethod
from contextlib import suppress
from pathlib import Path
from threading import Event
from time import sleep
from typing import ClassVar, Self

from celery import shared_task
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome

import _hook
from app.types import Dict
from bots.resources.driver import BotDriver
from bots.resources.iterators import BotIterator
from bots.resources.managers.credencial_manager import CredencialManager
from bots.resources.managers.file_manager import FileManager
from bots.resources.queues.file_operation import SaveError, SaveSuccess
from bots.resources.queues.print_message import PrintMessage
from constants import WORKDIR

__all__ = ["_hook"]


class CrawJUD:
    """Classe CrawJUD."""

    bots: ClassVar[dict[str, type[Self]]] = {}
    row: int = 0
    _total_rows: int = 0
    remaining: int = 0

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

    def setup(self, config: Dict) -> Self:
        self.config = config
        self.bot_stopped = Event()
        self.print_message = PrintMessage(self)
        self.append_success = SaveSuccess(self)
        self.append_error = SaveError(self)
        self.credenciais = CredencialManager(self)
        self.file_manager = FileManager(self)
        self.bot_driver = BotDriver(self)

        if config.get("credenciais"):
            self.credenciais.load_credenciais(self.config.get("credenciais"))
            if not self.auth():
                with suppress(Exception):
                    self.driver.quit()

        if config.get("planilha_xlsx"):
            self.file_manager.download_files()
            self.frame = BotIterator(self)

        return self

    def finalize_execution(self) -> None:
        with suppress(Exception):
            window_handles = self.driver.window_handles
            if window_handles:
                self.driver.delete_all_cookies()
                self.driver.quit()

        message = "Fim da execução"
        self.print_message(message=message, message_type="success")

        link = self.file_manager.upload_file()

        message = f"Baixe os resultados aqui: {link}"
        self.print_message(message=message, message_type="info")

        sleep(5)

        self.print_message.queue_print_bot.shutdown()

    @abstractmethod
    def auth(self) -> bool:
        """Autenticação no sistema."""
        ...

    @abstractmethod
    def execution(self) -> None: ...

    @property
    def driver(self) -> WebDriver | Chrome:
        return self.bot_driver.driver

    @property
    def wait(self) -> WebDriverWait[WebDriver | Chrome]:
        return self.bot_driver.wait

    @property
    def output_dir_path(self) -> Path:
        out_dir = WORKDIR.joinpath("output", self.pid)
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    @property
    def planilha_xlsx(self) -> str:
        return self.config.get("planilha_xlsx")

    @planilha_xlsx.setter
    def planilha_xlsx(self, val: str) -> None:
        self.config.update({"planilha_xlsx": val})

    @property
    def pid(self) -> str:
        return self.config.get("pid")

    @property
    def anexos(self) -> list[str]:
        return self.config.get("anexos")

    @property
    def total_rows(self) -> int:
        return self._total_rows

    @total_rows.setter
    def total_rows(self, value: int) -> None:
        self.remaining = value
        self._total_rows = value


@shared_task(name="crawjud")
def start_bot(config: Dict) -> None:
    bot_nome = f"{config['categoria']}_{config['sistema']}"
    bot = CrawJUD.bots[bot_nome]()
    return bot.setup(config=config).execution()
