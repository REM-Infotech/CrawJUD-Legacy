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
        """Formata mensagem de log com PID, tipo, linha e horário.

        Args:
            pid (str): Identificador do processo.
            message_type (MessageType): Tipo da mensagem.
            row (int): Linha do evento.

        Returns:
            Self: Instância atual com mensagem formatada.

        """
        # Extrai os primeiros 6 caracteres do PID
        # e converte para maiúsculo
        pid = pid[:6].upper()
        # Define o fuso horário para São Paulo
        tz = ZoneInfo("America/Sao_Paulo")
        # Obtém o horário atual formatado
        time_ = datetime.now(tz=tz).strftime("%H:%M:%S")

        # Monta a mensagem de log formatada
        msg = f"[({pid}, {message_type}, {row}, {time_})> {self.data}]"

        # Atualiza o atributo data da UserString
        self.data = msg
        return self
