from socketio import Client
from time import sleep

io = Client()


class SocketBot:
    def __init__(self):
        self.connected = False

    def with_context(self, event: str, data: dict, url: str):
        url = f"https://{url}"

        # Verifica se já está conectado antes de tentar se conectar
        if not self.connected:
            io.connect(url, namespaces=["/log"], retry=True)
            self.connected = True

        io.emit(event, data, "/log")
        sleep(1)

        # Após a emissão, desconecta e define o status
        io.disconnect()
        self.connected = False

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
