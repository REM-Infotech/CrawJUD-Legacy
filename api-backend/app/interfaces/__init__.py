"""Defina interfaces e tipos compartilhados para o backend.

Este pacote contém definições de tipos e contratos para uso
em diferentes módulos do sistema.
"""

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from app.types import MessageType, StatusBot


class Message(TypedDict, total=False):
    """Defina o formato de mensagem trocada entre módulos do sistema."""

    pid: str
    message: str
    message_type: MessageType
    status: StatusBot
    start_time: str
    row: int
    total: int
    error_count: int
    success_count: int
    remaining_count: int
