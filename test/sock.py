import inquirer
import socketio
from socketio.exceptions import BadNamespaceError, ConnectionError

connected = False
io = socketio.Client()


class SocketBot:

    def __init__(self):

        # Registra os eventos na inicialização
        io.on("connect", self.on_connect)
        io.on("disconnect", self.on_disconnect)

    def on_connect(self):
        print("Conectado!")
        # Fazer o join na sala ao conectar
        io.emit("join", {"pid": "N3T7R9"})

    def on_disconnect(self):
        print("Desconectado!")
        # Sair da sala ao desconectar
        io.emit("leave", {"pid": "N3T7R9"})

    def send_message(self, data):
        global connected
        try:
            if not connected:
                io.connect("https://back.robotz.dev", namespaces=["/log"])
                connected = True
            # Adiciona o 'pid' aos dados e envia a mensagem
            data.update({"pid": "N3T7R9"})
            io.emit("log_message", data, namespace="/log")
        except (BadNamespaceError, ConnectionError) as e:
            print(f"Erro de conexão: {e}")
            if not all([hasattr(e, "args"), "Already connected" in e.args]):
                connected = False  # Marca como desconectado para tentar reconectar

    def prompt(self):
        while True:
            quest = [inquirer.Text("message", "Mensagem para o socket")]
            prompt = inquirer.prompt(quest)
            if prompt:
                self.send_message(data=prompt)


if __name__ == "__main__":
    bot = SocketBot()
    bot.prompt()
