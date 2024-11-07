import os
import pytz
import logging
from tqdm import tqdm
from time import sleep
from datetime import datetime
from .socketio import SocketBot
from dotenv import dotenv_values
from ...CrawJUD import CrawJUD

codificacao = "UTF-8"
mensagens = []

url_socket = dotenv_values().get("HOST")


class printbot(CrawJUD):

    iobot = SocketBot()

    def __init__(self):
        """### PrintLogs"""

    def print_msg(self):

        log = self.message
        if self.message_error:
            log = self.message_error
            self.message_error = None

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
        }

        self.socket_message(data)
        mensagens.append(self.prompt)

        self.list_messages = mensagens
        if "fim da execução" in self.message.lower():
            sleep(1)
            self.file_log()

    def file_log(self) -> None:

        try:
            savelog = os.path.join(
                os.getcwd(), "Temp", self.pid, f"LogFile - PID {self.pid}.txt"
            )
            with open(savelog, "a") as f:
                for mensagem in self.list_messages:

                    if self.pid in mensagem:
                        f.write(f"{mensagem}\n")
                pass

        except Exception as e:
            # Aguarda 2 segundos
            sleep(2)

            # Registra o erro
            logging.error(f"Exception: {e}", exc_info=True)

            # Exibe o erro
            tqdm.write(f"{e}")

    def end_bot(self, status: str) -> None:

        data = {"pid": self.pid, "status": status}

        self.iobot.end_message(data, url_socket)

    def socket_message(self, data: dict) -> None:

        chk_type1 = "fim da execução" in self.prompt
        chk_type2 = "falha ao iniciar" in self.prompt
        message_stop = [chk_type1, chk_type2]

        try:

            if any(message_stop):
                data.update({"system": self.system, "typebot": self.typebot})

            self.iobot.send_message(data, url_socket)

        except Exception as e:
            print(e)
