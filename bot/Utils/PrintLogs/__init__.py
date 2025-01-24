import logging
import os
import pathlib
from datetime import datetime
from time import sleep

import pytz
from dotenv import dotenv_values
from tqdm import tqdm

from ...shared import PropertiesCrawJUD
from .socketio import SocketBot

codificacao = "UTF-8"
mensagens = []

url_socket = dotenv_values().get("HOSTNAME")
iobot = SocketBot()


class printbot(PropertiesCrawJUD):

    @classmethod
    def print_msg(cls) -> None:

        log = cls.message
        if cls.message_error:
            log = cls.message_error
            cls.message_error = None

        cls.prompt = "[({pid}, {type_log}, {row}, {dateTime})> {log}]".format(
            pid=cls.pid,
            type_log=cls.type_log,
            row=cls.row,
            dateTime=datetime.now(pytz.timezone("America/Manaus")).strftime("%H:%M:%S"),
            log=log,
        )
        tqdm.write(cls.prompt)

        data: dict[str, str | int] = {
            "message": cls.prompt,
            "pid": cls.pid,
            "type": cls.type_log,
            "pos": cls.row,
            "graphicMode": cls.graphicMode,
            "total": cls.kwrgs.get("total_rows", 0),
        }

        cls().socket_message(data)
        mensagens.append(cls.prompt)

        cls.list_messages = mensagens
        if "fim da execução" in cls.message.lower():
            sleep(1)
            cls.file_log()

    def file_log(cls) -> None:

        try:
            savelog = os.path.join(
                pathlib.Path(__file__).cwd(),
                "exec",
                cls.pid,
                f"LogFile - PID {cls.pid}.txt",
            )
            with open(savelog, "a") as f:
                for mensagem in cls.list_messages:

                    if cls.pid in mensagem:
                        f.write(f"{mensagem}\n")
                pass

        except Exception as e:
            # Aguarda 2 segundos
            sleep(2)

            # Registra o erro
            logging.error(f"Exception: {e}", exc_info=True)

            # Exibe o erro
            tqdm.write(f"{e}")

    def end_bot(cls, status: str) -> None:

        data = {"pid": cls.pid, "status": status}

        iobot.end_message(data, url_socket)

    @classmethod
    def socket_message(cls, data: dict) -> None:

        chk_type1 = "fim da execução" in cls.prompt
        chk_type2 = "falha ao iniciar" in cls.prompt
        message_stop = [chk_type1, chk_type2]

        try:

            if any(message_stop):
                data.update({"system": cls.system, "typebot": cls.typebot})

            iobot.send_message(data, url_socket)

        except Exception as e:
            print(e)
