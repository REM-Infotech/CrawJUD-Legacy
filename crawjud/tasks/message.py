"""Tarefas relacionadas ao envio de mensagens de log para o sistema de monitoramento.

Este módulo contém a classe PrintMessage, responsável por enviar mensagens de log
assíncronas via Socket.IO, permitindo a comunicação em tempo real com o sistema de
monitoramento.
"""

from __future__ import annotations

from contextlib import suppress
from pathlib import Path

from dotenv import dotenv_values
from socketio import AsyncSimpleClient

from crawjud.decorators import shared_task

environ = dotenv_values()
workdir_path = Path(__file__).cwd()
server = environ.get("SOCKETIO_SERVER_URL", "http://localhost:5000")
namespace = environ.get("SOCKETIO_SERVER_NAMESPACE", "/")

transports = ["websocket"]
headers = {"Content-Type": "application/json"}


@shared_task(name="print_message")
async def print_msg(
    event: str = "log_execution",
    data: dict[str, str] | str | None = None,
    room: str | None = None,
) -> None:
    """Envia mensagem assíncrona para o sistema de monitoramento via Socket.IO.

    Args:
        event (str): Evento a ser emitido (padrão: "log_execution").
        data (dict[str, str] | str): Dados da mensagem a ser enviada.
        room (str): Sala para envio da mensagem (opcional).
        *args: Argumentos posicionais adicionais.
        **kwargs: Argumentos nomeados adicionais.



    """
    async with AsyncSimpleClient() as sio:
        with suppress(Exception):
            # Cria uma instância do cliente Socket.IO e conecta ao servidor
            # com o namespace e cabeçalhos especificados.
            # Se uma sala for especificada, o cliente se juntará a ela.
            # Em seguida, emite o evento com os dados fornecidos.

            await sio.connect(
                url=server,
                transports=transports,
                namespace=namespace,
            )
            # Se uma sala for especificada, o cliente se juntará a ela.
            if room:
                join_data = {"data": {"room": room}}
                await sio.emit("join_room", data=join_data)

            # Emite o evento com os dados fornecidos.
            await sio.emit(event, data={"data": data})
