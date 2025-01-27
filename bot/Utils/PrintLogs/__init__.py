import logging
import os
import pathlib
from datetime import datetime
from time import sleep
from typing import Self

import pytz
from dotenv import dotenv_values
from tqdm import tqdm

from ...core import CrawJUD
from .socketio import SocketBot

codificacao = "UTF-8"
mensagens = []

url_socket = dotenv_values().get("HOSTNAME")
iobot = SocketBot()


class PrintBot(CrawJUD):

    def __init__(
        self,
    ) -> None:
        """"""

    def print_msg(self) -> None:

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
        tqdm.write(self.prompt)

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

        try:
            savelog = os.path.join(
                pathlib.Path(__file__).cwd(),
                "exec",
                self.pid,
                f"LogFile - PID {self.pid}.txt",
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

    def end_prt(self, status: str) -> None:

        data = {"pid": self.pid, "status": status}

        iobot.end_message(data, url_socket)

    @classmethod
    def socket_message(cls, self: Self, data: dict) -> None:

        chk_type1 = "fim da execução" in self.prompt
        chk_type2 = "falha ao iniciar" in self.prompt
        message_stop = [chk_type1, chk_type2]

        try:

            if any(message_stop):
                data.update({"system": self.system, "typebot": self.typebot})

            iobot.send_message(data, url_socket)

        except Exception as e:
            print(e)
