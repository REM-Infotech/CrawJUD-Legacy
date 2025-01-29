# from time import sleep
from time import sleep

from socketio import Client

sio = Client()


class SocketBot:
    def __init__(self) -> None:
        self.connected = False
        self.tries = 0

    def with_context(self, event: str, data: dict, url: str) -> None:
        try:
            url = f"https://{url}"

            """Verifica se já está conectado antes de tentar se conectar"""
            self.connect_emit(event, data, url)

        except Exception:
            # print(e)
            try:
                self.connected = False
                sio.disconnect()
                sleep(0.25)
                self.connect_emit(event, data, url)

            except Exception:
                sleep(0.25)
                # self.connect_emit(event, data, url)

        # with app.app_context():
        #     io.emit(event, data, namespace="/log")

    def connect_emit(self, event: str, data: dict, url: str) -> None:
        if not self.connected:
            sio.connect(url, namespaces=["/log"])
            self.connected = True

        sio.emit(event, data, namespace="/log")

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
