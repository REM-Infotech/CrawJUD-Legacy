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
import socketio.exceptions
from dotenv_vault import load_dotenv

from ...core import CrawJUD

codificacao = "UTF-8"
mensagens = []
load_dotenv()


url_socket = environ.get("HOSTNAME")


class PrintBot(CrawJUD):
    """Handle printing logs and sending log messages via SocketBot.

    Inherit from CrawJUD and provide methods to print, emit, and store logs.
    """

    def __init__(self) -> None:
        """Initialize the PrintBot instance with default settings.

        No parameters.
        """

    def print_msg(self) -> None:
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

        data: dict[str, str | int] = {
            "message": self.prompt,
            "pid": self.pid,
            "type": self.type_log,
            "pos": self.row,
            "graphicMode": self.graphicMode,
            "total": self.total_rows,
        }

        self.list_messages = mensagens
        if "fim da execução" in self.message.lower():
            sleep(1)
            self.file_log(self)

        self.socket_message(data)
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

    def end_prt(self, status: str) -> None:
        """Send final status message for termination.

        Prepares the final data package and emits a status signal.

        Args:
            status (str): The final status message indicator.

        """
        data = {"pid": self.pid, "status": status}
        self.end_message(data, url_socket)

    def socket_message(self: Self, data: dict) -> None:
        """Emit log message to the socket with termination checks.

        Updates data with system info if termination patterns are detected and
        sends the message through the socket.

        Args:
            data (dict): Dictionary containing log details.

        """
        chk_type1 = "fim da execução" in self.prompt
        chk_type2 = "falha ao iniciar" in self.prompt
        message_stop = [chk_type1, chk_type2]

        try:
            if any(message_stop):
                data.update({"system": self.system, "typebot": self.typebot})
            self.send_message(data, url_socket)

        except Exception:
            err = traceback.format_exc()
            self.logger.exception(err)

    def with_context(self, event: str, data: dict, url: str) -> None:  # noqa: C901
        """Emit event with data via socket ensuring proper connection context.

        Attempts connection if not already connected and manages retries on errors.

        Args:
            event (str): The event to emit.
            data (dict): The data to send.
            url (str): The socket server URL.

        """
        err = None

        try:
            url = f"https://{url}"
            # Verifica se já está conectado antes de tentar se conectar
            if self.connected is False:
                self.connect_socket(url)
            sleep(0.5)
            self.emit_message(event, data)
            sleep(1)

        except socketio.exceptions.BadNamespaceError as e:
            err = str(e)
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
                err = str(e)

        except socketio.exceptions.ConnectionError as e:
            err = str(e)
            try:
                if "One or more namespaces failed to connect" in str(e):
                    sleep(1)
                    self.connected = False
                    self.connect_socket(url)
                    self.emit_message(event, data)
                elif "Already connected" in str(e):
                    self.emit_message(event, data)
                    self.connected = True
            except Exception as e:
                err = str(e)

        except Exception as e:
            err = str(e)

        if err:
            self.logger.error(err)

    def emit_message(self, event: str, data: dict) -> None:
        """Emit an event with its associated data on the log namespace.

        Args:
            event (str): The event identifier.
            data (dict): The data payload to be sent.

        """
        self.sio.emit(event, data, namespace="/log")

    def connect_socket(self, url: str) -> None:
        """Connect to the socket server using the specified URL and headers.

        Includes the process id as a header for identification.

        Args:
            url (str): The server URL.

        """
        self.sio.connect(url, namespaces=["/log"], headers={"pid": self.pid})

    def send_message(self, data: dict[str, str | int], url: str) -> None:
        """Send a log message by embedding context details via with_context.

        Args:
            data (dict[str, str | int]): The message details.
            url (str): The socket server URL.

        """
        self.with_context("log_message", data, url)

    def end_message(self, data: dict, url: str) -> None:
        """Finalize the process by emitting stop and status messages.

        Uses a try-finally construct to ensure both events are sent.

        Args:
            data (dict): Final message data.
            url (str): The socket server URL.

        """
        try:
            pass
        finally:
            self.with_context("stop_bot", data, url)
            self.with_context("statusbot", {}, url)
