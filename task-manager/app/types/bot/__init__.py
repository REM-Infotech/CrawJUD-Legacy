"""Tipos Customizados para os Robôs."""

from collections import UserString
from datetime import datetime
from typing import Literal, Self
from zoneinfo import ZoneInfo

type MessageType = Literal["info", "log", "error", "warning", "success"]


class MessageLog(UserString):
    """Classe para manipular mensagens de log formatadas e tipadas.

    Esta classe herda de UserString e permite formatar mensagens de log
    com informações de identificação, tipo de mensagem, linha e horário
    de execução, facilitando o rastreamento e auditoria de eventos.


    """

    def format(
        self,
        pid: str,
        message_type: MessageType,
        row: int,
    ) -> Self:
        # Extrai os primeiros 6 caracteres do PID e converte para maiúsculo
        mini_pid = pid[:6].upper()
        # Define o fuso horário para São Paulo
        tz = ZoneInfo("America/Sao_Paulo")
        # Obtém o horário atual formatado
        time_exec = datetime.now(tz=tz).strftime("%H:%M:%S")

        # Monta a mensagem de log formatada
        msg = f"[({mini_pid}, {message_type}, {row}, {time_exec})> {self}]"

        # Atualiza o atributo data da UserString
        self.data = msg
        return self
