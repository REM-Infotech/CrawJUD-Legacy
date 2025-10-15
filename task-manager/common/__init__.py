"""Fornece funcionalidades comuns para o aplicativo CrawJUD.

Este pacote contém módulos utilitários e funções compartilhadas entre
diferentes partes do sistema.
"""

from typing import NoReturn


def _raise_execution_error(message: str) -> NoReturn:
    from common.exceptions import ExecutionError

    raise ExecutionError(message=message)


__all__ = ["_raise_execution_error"]
