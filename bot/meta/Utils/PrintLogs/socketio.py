# from time import sleep
from app import io, app
from status.server_side import serverSide


class SocketBot:
    def __init__(self):
        self.connected = False
        self.first_log = 0

    def with_context(self, event: str, data: dict, url: str):
        # url = f"https://{url}"

        # Verifica se já está conectado antes de tentar se conectar
        # if not self.connected:
        #     sio.connect(url, namespaces=["/log"], retry=True)
        #     self.connected = True

        # sio.emit(event, data, "/log")
        # sleep(1)

        # Após a emissão, desconecta e define o status
        # io.disconnect()
        # self.connected = False
        data = serverSide(data, data["pid"])
        with app.app_context():
            io.emit(event, data, namespace="/log")

    def send_message(self, data: dict[str, str | int], url: str):
        try:
            pass
        finally:
            self.with_context("log_message", data, url)

    def end_message(self, data: dict, url: str):
        try:
            pass
        finally:
            self.with_context("stop_bot", data, url)
