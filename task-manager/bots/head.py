"""Abstração CrawJUD."""

from __future__ import annotations

from abc import abstractmethod
from contextlib import suppress
from threading import Event

from celery import Task
from resources.queues.file_operation import SaveError, SaveSuccess
from resources.queues.print_message import PrintMessage

import _hook
from bots.resources._formatadores import formata_string
from bots.resources.managers.credencial_manager import CredencialManager
from bots.resources.managers.file_manager import FileManager

__all__ = ["_hook"]


@PropertyCrawJUD()
class CrawJUD(Task):
    """Classe CrawJUD."""

    def __init__(self) -> None:
        """Inicializa o CrawJUD."""
        self._task = self.run
        self.run = self.setup

    def setup(self) -> None:
        self._bot_stopped = Event()
        self.print_message = PrintMessage(self)
        self.append_succes = SaveSuccess(self)
        self.append_error = SaveError(self)
        self.credenciais = CredencialManager(self)
        self.file_manager = FileManager(self)

        self.file_manager.download_files()
        self.credenciais.load_credenciais()

        if not self.auth():
            with suppress(Exception):
                self.driver.quit()

        if self.anexos:
            self._anexos = [
                formata_string(anexo) for anexo in list(self._anexos)
            ]

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
