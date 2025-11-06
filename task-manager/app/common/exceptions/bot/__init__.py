"""Módulo de controle de exceptions dos bots."""

import traceback

from common.exceptions import BaseCrawJUDError as BaseCrawJUDError

MessageError = "Erro ao executar operaçao: "


def formata_msg(exc: Exception | None = None) -> str:
    """Formata mensagem de erro detalhada a partir de uma exceção fornecida ao bot.

    Args:
        exc (Exception | None): Exceção a ser formatada, se fornecida.

    Returns:
        str: Mensagem formatada contendo detalhes da exceção, se houver.

    """
    if exc:
        return "\n Exception: " + "\n".join(
            traceback.format_exception_only(exc),
        )

    return ""
