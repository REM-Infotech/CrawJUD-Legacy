# from time import sleep
from socketio import Client
from status.server_side import serverSide

sio = Client()


class SocketBot:
    def __init__(self):
        self.connected = False
        self.first_log = 0

    def with_context(self, event: str, data: dict, url: str):

        data = serverSide(data, data["pid"])
        url = f"https://{url}"

        """Verifica se já está conectado antes de tentar se conectar"""
        if not self.connected:
            sio.connect(url, namespaces=["/log"], retry=True)
            self.connected = True

        sio.connect(url, namespace="/log")
        sio.emit(event, data)

        sio.sleep(0.25)

        """Após a emissão, desconecta e define o status"""
        sio.disconnect()
        self.connected = False

        # with app.app_context():
        #     io.emit(event, data, namespace="/log")

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
