"""Module: PrintLogs.

Provides logging and message handling utilities for the CrawJUD project.
Additional utilities are available to emit, print, and store log messages.
"""

import traceback
from datetime import datetime
from os import environ
from pathlib import Path
from threading import Thread  # noqa: F401
from time import sleep
from typing import Self

import pytz
import socketio
import socketio.exceptions  # noqa: F401
from dotenv_vault import load_dotenv

from ...core import CrawJUD
from .emit_ import SendMessage

codificacao = "UTF-8"
mensagens = []
load_dotenv()


class PrintBot(CrawJUD):
    """Handle printing logs and sending log messages via SocketIo.

    Inherit from CrawJUD and provide methods to print, emit, and store logs.
    """

    def __init__(self) -> None:
        """Initialize the PrintBot instance with default settings.

        No parameters.
        """

    def print_msg(self, status_bot: str = "Em Execução") -> None:
        """Print current log message and emit it via the socket.

        Uses internal message attributes, logs the formatted string,
        and appends the output to the messages list.
        """
        log = self.message
        if self.message_error:
            log = self.message_error
            self.message_error = ""

        self.prompt = "[({pid}, {type_log}, {row}, {dateTime})> {log}]".format(
            pid=self.pid,
            type_log=self.type_log,
            row=self.row,
            dateTime=datetime.now(pytz.timezone("America/Manaus")).strftime("%H:%M:%S"),
            log=log,
        )
        self.logger.info(self.prompt)
        self.list_messages = mensagens
        if "fim da execução" in self.message.lower():
            sleep(1)
            self.file_log(self)

        self.sendmsg.setup_message(status_bot=status_bot)
        mensagens.append(self.prompt)

    @classmethod
    def file_log(cls, self: Self) -> None:
        """Write log messages to a file based on the list_messages attribute.

        Opens (or creates) a log file specific to the process id and writes
        each relevant message.

        Args:
            self (Self): The current PrintBot instance.

        """
        try:
            savelog = Path(self.output_dir_path).resolve().joinpath(f"LogFile - PID {self.pid}.txt")
            with savelog.open("a") as f:
                for mensagem in self.list_messages:
                    if self.pid in mensagem:
                        f.write(f"{mensagem}\n")

        except Exception:
            # Aguarda 2 segundos
            sleep(2)
            err = traceback.format_exc()
            self.logger.exception(err)
