"""Module: PrintLogs.

This module provides logging and message handling utilities for the CrawJUD project.

"""

import logging
import os
import pathlib
import traceback
from datetime import datetime
from os import environ
from time import sleep
from typing import Self

import pytz
from dotenv_vault import load_dotenv
from tqdm import tqdm

from ...core import CrawJUD
from .socketio import SocketBot

codificacao = "UTF-8"
mensagens = []
load_dotenv()

url_socket = environ.get("HOSTNAME")
iobot = SocketBot()


class PrintBot(CrawJUD):
    """Handles printing logs and sending log messages via SocketBot."""

    def __init__(self) -> None:
        """Initialize a new PrintBot instance."""
        """"""

    def print_msg(self) -> None:
        """Print the current message and emit it to the socket."""
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
        tqdm.write(self.prompt)

        data: dict[str, str | int] = {
            "message": self.prompt,
            "pid": self.pid,
            "type": self.type_log,
            "pos": self.row,
            "graphicMode": self.graphicMode,
            "total": self.kwrgs.get("total_rows", 0),
        }

        PrintBot.socket_message(self, data)
        mensagens.append(self.prompt)

        self.list_messages = mensagens
        if "fim da execução" in self.message.lower():
            sleep(1)
            PrintBot.file_log(self)

    @classmethod
    def file_log(cls, self: Self) -> None:
        """Write log messages to a file."""
        try:
            savelog = os.path.join(pathlib.Path(__file__).cwd(), "exec", self.pid, f"LogFile - PID {self.pid}.txt")
            with open(savelog, "a") as f:
                for mensagem in self.list_messages:
                    if self.pid in mensagem:
                        f.write(f"{mensagem}\n")

        except Exception:
            # Aguarda 2 segundos
            sleep(2)

            err = traceback.format_exc()

            # Registra o erro
            logging.exception(err)

    def end_prt(self, status: str) -> None:
        """Send a final status message."""
        data = {"pid": self.pid, "status": status}

        iobot.end_message(data, url_socket)

    @classmethod
    def socket_message(cls, self: Self, data: dict) -> None:
        """Send a message to the socket and handle termination checks."""
        chk_type1 = "fim da execução" in self.prompt
        chk_type2 = "falha ao iniciar" in self.prompt
        message_stop = [chk_type1, chk_type2]

        try:
            if any(message_stop):
                data.update({"system": self.system, "typebot": self.typebot})

            iobot.send_message(data, url_socket)

        except Exception:
            err = traceback.format_exc()
            logging.exception(err)
