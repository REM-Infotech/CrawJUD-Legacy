"""Módulo de interfaces para o CrawJUD."""

from collections.abc import Callable
from typing import TypedDict

from crawjud.interfaces.types.literals import (
    MsgUsuarioAtualizado,
    MsgUsuarioCadastrado,
    MsgUsuarioDeletado,
)


class ActionsDict(TypedDict):
    """Defina o dicionário de ações para manipulação de usuários no CrawJUD.

    Args:
        INSERT (Callable[[dict], MsgUsuarioCadastrado]): Insere um novo usuário.
        UPDATE (Callable[[dict], MsgUsuarioAtualizado]): Atualiza um usuário existente.
        DELETE (Callable[[dict], MsgUsuarioDeletado]): Remove um usuário do sistema.

    Returns:
        TypedDict: Estrutura contendo as funções de manipulação de usuários.

    """

    INSERT: Callable[[dict], MsgUsuarioCadastrado]
    UPDATE: Callable[[dict], MsgUsuarioAtualizado]
    DELETE: Callable[[dict], MsgUsuarioDeletado]
