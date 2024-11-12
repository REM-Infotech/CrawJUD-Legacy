import socketio
from time import sleep
from socketio.exceptions import BadNamespaceError, ConnectionError

connected = False


class SocketBot:

    pid = ""

    def __init__(self):
        # Registra os eventos na inicialização
        self.io = socketio.Client()
        self.io.on("connect", self.on_connect)
        self.io.on("disconnect", self.on_disconnect)

    def on_connect(self):
        print("Conectado!")
        # Fazer o join na sala ao conectar
        self.io.emit("join", {"pid": "N3T7R9"}, namespace="/log")

    def on_disconnect(self):
        print("Desconectado!")
        # Sair da sala ao desconectar
        self.io.emit("leave", {"pid": "N3T7R9"}, namespace="/log")

    def send_message(self, data: dict[str, str | int], url):

        sleep(0.5)
        global connected

        try:
            self.pid = data["pid"]
            if not connected:

                try:
                    self.io.connect(
                        f"https://{url}",
                        namespaces=["/log"],
                        transports=["websocket"],
                    )
                    connected = True
                except Exception as e:
                    if "already connected" in str(e).lower():
                        connected = True
                    else:
                        raise e

            # Adiciona o 'pid' aos dados e envia a mensagem
            self.io.emit("log_message", data, namespace="/log")
        except (BadNamespaceError, ConnectionError) as e:

            if type(e) is BadNamespaceError:
                self.io.disconnect()
                self.io.connect(
                    f"https://{url}",
                    namespaces=["/log"],
                )
                connected = True
                self.io.emit("log_message", data, namespace="/log")
                print(f"Erro de conexão: {e}")

    def end_message(self, data: dict, url):
        global connected

        try:
            self.pid = data["pid"]
            if not connected:
                self.io.connect(
                    f"https://{url}",
                    namespaces=["/log"],
                    transports=["websocket"],
                )
                connected = True
            # Adiciona o 'pid' aos dados e envia a mensagem
            self.io.emit("stop_bot", data, namespace="/log")
        except (BadNamespaceError, ConnectionError) as e:
            print(f"Erro de conexão: {e}")
            connected = False
            self.io.disconnect()
            self.send_message(data, url)

    def prompt(self):
        while True:
            quest = [inquirer.Text("message", "Mensagem para o socket")]
            prompt = inquirer.prompt(quest)
            if prompt:
                self.send_message(data=prompt)


if __name__ == "__main__":
    import inquirer

    bot = SocketBot()
    bot.prompt()
