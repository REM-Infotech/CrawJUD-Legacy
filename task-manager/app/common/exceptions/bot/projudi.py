"""Projudi bot exceptions."""

from typing import ClassVar, Literal

from app.common.exceptions import BaseCrawJUDError

type MessageTokenError = Literal["Senha do Token Incorreta"]


class PasswordTokenError(BaseCrawJUDError):
    """Handler de erro de senha de token Projudi."""

    message: ClassVar[str] = ""

    def __init__(
        self,
        message: MessageTokenError = "Senha do Token Incorreta",
    ) -> None:
        """Inicializa a mensagem de erro."""
        self.message = message
        super().__init__(message)
