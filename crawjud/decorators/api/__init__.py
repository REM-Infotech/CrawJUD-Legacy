"""Fornece decoradores e funções utilitárias para manipulação de CORS.

Este módulo inclui:
- Decoradores para validação de JWT em WebSocket.
- Funções para normalização de métodos, cabeçalhos e origem para CORS.
- Função para adicionar cabeçalhos CORS às respostas HTTP.
"""

from __future__ import annotations

import functools
from contextlib import suppress
from typing import TYPE_CHECKING

from quart import (
    request,
)
from quart_jwt_extended import decode_token

from .cross_origin import CrossDomain

if TYPE_CHECKING:
    from collections.abc import Callable

    from crawjud.interfaces.types import P, T


def verify_jwt_websocket(func: Callable[P, T]) -> Callable[P, T]:
    """Valida o token JWT presente nos cookies da requisição WebSocket.

    Args:
        func (Callable): Função assíncrona a ser decorada.

    Returns:
        Função decorada que verifica o JWT antes
            de executar a função original.

    Observações:
        Emite o evento "not_logged" no namespace "/main" caso o token seja inválido.

    """

    @functools.wraps(func)
    async def decorated_function(*args: P.args, **kwargs: P.kwargs) -> T:
        valid = False
        with suppress(Exception):
            valid = True
            decode_token(
                request.cookies["access_token_cookie"],
                request.cookies["X-Xsrf-Token"],
            )
            valid = True

        if not valid:
            from app import io

            await io.emit("not_logged", namespace="/master")
            return []

        return await func(*args, **kwargs)

    return decorated_function


__all__ = ["CrossDomain", "verify_jwt_websocket"]
