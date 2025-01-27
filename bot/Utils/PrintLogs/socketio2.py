# from time import sleep
import traceback
from time import sleep
from typing import Dict

from socketio import Client
from socketio.exceptions import BadNamespaceError, ConnectionError

sio = Client(reconnection_attempts=5)


@sio.on("connect", namespace="*")
def on_connect(namespace=None, client_=None) -> None:
    sleep(0.25)


@sio.on("disconnect", namespace="*")
def on_disconnect(namespace=None, client_=None) -> None:
    sleep(0.25)


@sio.on("log_message", namespace="*")
def on_message(data: dict, namespace=None, client_=None) -> None:
    sleep(0.25)


@sio.on("stop_bot", namespace="*")
def on_stop_bot(data: dict, namespace=None, client_=None) -> None:
    sleep(0.25)


class SocketBot:
    def __init__(self) -> None:
        self.connected = False
        self.tries = 0

    def with_context(self, event: str, data: Dict, url: str) -> None:
        exc = None

        try:
            url = f"https://{url}"

            """Verifica se já está conectado antes de tentar se conectar"""
            self.connect_socket(url)
            sleep(0.5)
            self.emit_message(event, data)
            sleep(1)

        except BadNamespaceError:

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
                    sio.disconnect()
                    self.connected = False
                    sleep(1)
                    self.connect_socket(url)
                    sleep(0.5)
                    self.emit_message(event, data)
                    sleep(1)

                exc = traceback.format_exc()

        except ConnectionError as e:

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
            print(exc)

    def emit_message(self, event: str, data: Dict):

        sio.emit(event, data, namespace="/log")

    def connect_socket(self, url: str) -> None:

        if self.connected is False:
            sio.connect(url, namespaces=["/log"])
            self.connected = True

    def send_message(self, data: dict[str, str | int], url: str) -> None:
        try:
            pass
        finally:
            self.with_context("log_message", data, url)

    def end_message(self, data: dict, url: str) -> None:
        try:
            pass
        finally:
            self.with_context("stop_bot", data, url)
            self.with_context("statusbot", {}, url)
