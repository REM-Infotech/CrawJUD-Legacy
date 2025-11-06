"""Fornece tipos e utilitários para manipulação de strings."""

import re
from collections import UserString
from contextlib import suppress
from datetime import datetime
from typing import TYPE_CHECKING, Literal, Self
from zoneinfo import ZoneInfo

from common._raises import value_error
from constants import PADRAO_CNJ

if TYPE_CHECKING:
    from app.types import AnyType

type MessageType = Literal["info", "log", "error", "warning", "success"]


class ProcessoCNJ(UserString):
    """Classe(str) ProcessoCNJ para processos no padrão CNJ."""

    def __init__(self, seq: str) -> None:
        """Inicializa a classe StrTime."""
        super().__init__(seq)
        self.__validate_str()

        seq = re.sub(
            r"(\d{7})(\d{2})(\d{4})(\d)(\d{2})(\d{4})",
            r"\1-\2.\3.\4.\5.\6",
            seq,
        )

    def __validate_str(self) -> bool:
        matches = [re.match(pattern, self.data) for pattern in PADRAO_CNJ]

        return any(matches) or value_error()

    @property
    def tj(self) -> str:
        """Extrai o ID do TJ.

        Returns:
            str: TJ ID

        """
        to_return = None
        match_ = re.search(r"\.(\d)\.(\d{1,2})\.", self.data)
        if not match_:
            value_error()

        to_return: str = match_.group(2)
        if to_return.startswith("0"):
            to_return = to_return.replace("0", "")

        return to_return

    def __str__(self) -> str:
        """Retorne a representação em string da instância StrTime.

        Returns:
            str: Representação textual da instância.

        """
        return self.data

    def __instancecheck__(self, instance: AnyType) -> bool:
        """Verifique se a instância corresponde a padrões de string CNJ.

        Args:
            instance: Instância a ser verificada.

        Returns:
            bool: Indica se a instância corresponde a algum dos padrões de string CNJ.

        """
        with suppress(ValueError):
            matches = [re.match(pattern, instance) for pattern in PADRAO_CNJ]
            return any(matches) or value_error()

        return False


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
