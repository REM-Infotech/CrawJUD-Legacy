"""Exceções customizadas para operações de banco de dados em módulos internos.

Fornece classes de exceção específicas para erros de exclusão, atualização e
inserção de registros, detalhando o rastreamento de exceções originais.

"""

from __future__ import annotations

import traceback


class DeleteError(Exception):
    """Exception raised when trying to delete the user itself."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str | None = None,
    ) -> None:
        """Initialize the exception."""
        if not message:
            message = "\n".join(traceback.format_exception(exc))

        self.message = message

    def __str__(self) -> str:
        """Retorna a representação em string da exceção.

        Returns:
            str: mensagem da exceção

        """
        return self.message


class UpdateError(Exception):
    """Exception raised when trying to update the user itself."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str | None = None,
    ) -> None:
        """Initialize the exception."""
        if not message:
            message = "\n".join(traceback.format_exception(exc))

        self.message = message

    def __str__(self) -> str:
        """Retorna a representação em string da exceção.

        Returns:
            str: mensagem da exceção

        """
        return self.message


class InsertError(Exception):
    """Exception raised when trying to insert the user itself."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str | None = None,
    ) -> None:
        """Initialize the exception."""
        if not message:
            message = "\n".join(traceback.format_exception(exc))

        self.message = message

    def __str__(self) -> str:
        """Retorna a representação em string da exceção.

        Returns:
            str: mensagem da exceção

        """
        return self.message
