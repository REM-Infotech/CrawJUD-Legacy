"""Sistema de envio de logs para o ClientUI."""

import traceback
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING, TypedDict

from dotenv import load_dotenv
from socketio import Client
from tqdm import tqdm

from app.bots.resources.iterators.queue import QueueIterator
from app.interfaces import Message
from app.types import MessageLog, MessageType
from config import config

if TYPE_CHECKING:
    from app.bots.head import CrawJUD

load_dotenv()


class Count(TypedDict):
    """Dicionario de contagem."""

    sucessos: int = 0
    remainign_count: int = 0
    erros: int = 0


class PrintMessage:
    """Envio de logs para o FrontEnd."""

    bot: CrawJUD
    _message_type: MessageType

    def __init__(self, bot: CrawJUD) -> None:
        """Instancia da queue de salvamento de sucessos."""
        self.bot = bot
        self.queue_print_bot = Queue()
        self.thread_print_bot = Thread(target=self.print_msg)
        self.thread_print_bot.start()
        self.succcess_count = 0
        self.erros = 0

    def __call__(
        self,
        message: str,
        message_type: MessageType,
        row: int = 0,
        link: str | None = None,
    ) -> None:
        """Envie mensagem formatada para a fila de logs.

        Args:
            message (str): Mensagem a ser enviada.
            message_type (MessageType): Tipo da mensagem.
            row (int): Linha do registro.
            link (str): Link do resultado (apenas no fim da execução)

        """
        mini_pid = self.bot.pid[:6].upper()

        if not row or row == 0:
            row = self.bot.row

        message = MessageLog(message).format(
            mini_pid,
            message_type,
            row,
        )

        msg = Message(
            pid=self.bot.pid,
            row=row,
            message=str(message),
            message_type=message_type,
            status="Em Execução",
            total=self.bot.total_rows,
            sucessos=self.calc_success(message_type),
            erros=self.calc_error(message_type),
            restantes=self.calc_remaining(message_type),
            link=link,
        )
        self.queue_print_bot.put_nowait(msg)

    def calc_success(self, message_type: MessageType) -> int:
        """Calcula o total de mensagens de sucesso.

        Args:
            message_type (MessageType): Tipo da mensagem.

        Returns:
            int: Quantidade de mensagens de sucesso.

        """
        if message_type == "success":
            self.succcess_count += 1

        return self.succcess_count

    def calc_error(self, message_type: MessageType) -> int:
        """Calcula o total de mensagens de erro.

        Args:
            message_type (MessageType): Tipo da mensagem.

        Returns:
            int: Quantidade de mensagens de erro.

        """
        if message_type == "error":
            self.erros += 1

        return self.erros

    def calc_remaining(self, message_type: MessageType) -> int:
        """Calcula o total de registros restantes.

        Args:
            message_type (MessageType): Tipo da mensagem.

        Returns:
            int: Quantidade de registros restantes.

        """
        check_msg_type = any([
            message_type == "success",
            message_type == "error",
        ])
        if check_msg_type and self.bot.remaining > 0:
            self.bot.remaining -= 1

        return self.bot.remaining

    def print_msg(self) -> None:
        """Envie mensagens de log para o servidor via socket.

        Esta função conecta ao servidor socketio e envia mensagens
        presentes na fila para o FrontEnd.

        """
        socketio_server = config.get("SOCKETIO_SERVER")
        sio = Client()

        sio.on(
            "bot_stop",
            lambda: self.bot.bot_stopped.set(),
            namespace="/bot_logs",
        )
        sio.connect(url=socketio_server, namespaces=["/bot_logs"])
        sio.emit(
            "join_room",
            data={"room": self.bot.pid},
            namespace="/bot_logs",
        )

        for data in QueueIterator[Message](self.queue_print_bot):
            if data:
                try:
                    sio.emit("logbot", data=data, namespace="/bot_logs")
                    tqdm.write(data["message"])
                except Exception as e:
                    exc = "\n".join(traceback.format_exception(e))
                    tqdm.write(exc)
