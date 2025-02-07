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
import socketio
import socketio.exceptions
from dotenv_vault import load_dotenv
from tqdm import tqdm

from ...core import CrawJUD

codificacao = "UTF-8"
mensagens = []
load_dotenv()


url_socket = environ.get("HOSTNAME")


class PrintBot(CrawJUD):
    """Handles printing logs and sending log messages via SocketBot."""

    def __init__(self) -> None:
        """Initialize a new PrintBot instance."""
        """"""

    def print_msg(self) -> None:
        """Print the current message and emit it to the socket."""
        logger = logging.getLogger(__name__)
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
        logger.info(self.prompt)

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

            logger = logging.getLogger(__name__)
            logger.exception(err)

    def end_prt(self, status: str) -> None:
        """Send a final status message."""
        data = {"pid": self.pid, "status": status}

        self.end_message(data, url_socket)

    def socket_message(self: Self, data: dict) -> None:
        """Send a message to the socket and handle termination checks."""
        chk_type1 = "fim da execução" in self.prompt
        chk_type2 = "falha ao iniciar" in self.prompt
        message_stop = [chk_type1, chk_type2]

        try:
            if any(message_stop):
                data.update({"system": self.system, "typebot": self.typebot})

            self.send_message(data, url_socket)

        except Exception:
            err = traceback.format_exc()
            logger = logging.getLogger(__name__)
            logger.exception(err)

    def with_context(self, event: str, data: dict, url: str) -> None:  # noqa: C901
        """Handle the context for connecting and emitting messages.

        Args:
            event (str): The event to emit.
            data (dict): The data to send with the event.
            url (str): The URL to connect to.

        """
        exc = None

        try:
            url = f"https://{url}"

            # Verifica se já está conectado antes de tentar se conectar

            if self.connected is False:
                self.connect_socket(url)

            sleep(0.5)
            self.emit_message(event, data)
            sleep(1)

        except socketio.exceptions.BadNamespaceError:
            exc = traceback.format_exc()

            try:
                self.connected = False
                sleep(1)
                self.connect_socket(url)
                sleep(0.5)
                self.emit_message(event, data)
                sleep(1)

            except Exception as e:
                if "Client is not in a disconnected state" in str(e):
                    self.sio.disconnect()
                    self.connected = False
                    sleep(1)
                    self.connect_socket(url)
                    sleep(0.5)
                    self.emit_message(event, data)
                    sleep(1)

                exc = traceback.format_exc()

        except socketio.exceptions.ConnectionError as e:
            exc = traceback.format_exc()

            try:
                if "One or more namespaces failed to connect" in str(e):
                    sleep(1)
                    self.connected = False
                    self.connect_socket(url)

                    self.emit_message(event, data)

                elif "Already connected" in str(e):
                    self.emit_message(event, data)
                    self.connected = True

            except Exception:
                exc = traceback.format_exc()

        except Exception:
            exc = traceback.format_exc()

        if exc:
            tqdm.write(exc)

    def emit_message(self, event: str, data: dict) -> None:
        """Emit a message to the socket.

        Args:
            event (str): The event to emit.
            data (dict): The data to send with the event.
            sio (SimpleClient): The SimpleClient instance.

        """
        self.sio.emit(event, data, namespace="/log")

    def connect_socket(self, url: str) -> None:
        """Connect to the socket.

        Args:
            url (str): The URL to connect to.
            sio (SimpleClient): The SimpleClient instance

        """
        self.sio.connect(url, namespaces=["/log"])
        self.sio.emit("join", {"pid": self.pid}, namespace="/log")

    def send_message(self, data: dict[str, str | int], url: str) -> None:
        """Send a log message.

        Args:
            data (dict[str, str | int]): The data to send.
            url (str): The URL to connect to.

        """
        self.with_context("log_message", data, url)

    def end_message(self, data: dict, url: str) -> None:
        """Send a stop bot message and a status bot message.

        Args:
            data (dict): The data to send.
            url (str): The URL to connect to.

        """
        try:
            pass
        finally:
            self.with_context("stop_bot", data, url)
            self.with_context("statusbot", {}, url)
