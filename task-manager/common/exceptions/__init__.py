"""Módulo de tratamento de exceptions do robô."""

import traceback
from typing import Literal, NoReturn

MessageError = "Erro ao executar operaçao: "
type MessageTokenError = Literal["Senha do Token Incorreta"]


class StartError(Exception):
    """Exception raised for errors that occur during the start of the bot."""

    def __init__(
        self,
        message: str = MessageError,
        exc: Exception | None = None,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


def raise_start_error(message: str) -> NoReturn:
    """Lança exceção StartError com mensagem personalizada fornecida.

    Args:
        message (str): Mensagem de erro a ser exibida na exceção.

    Raises:
        StartError: Exceção lançada com a mensagem informada.

    """
    raise StartError(message=message)


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


class BaseCrawJUDError(Exception):
    """Base exception class for CrawJUD-specific errors."""


class DriverNotCreatedError(BaseCrawJUDError):
    """Handler de erro de inicialização do WebDriver."""


class AuthenticationError(BaseCrawJUDError):
    """Handler de erro de autenticação."""

    def __init__(self, message: str = "Erro de autenticação.") -> None:
        """Inicializa a mensagem de erro."""
        super().__init__(message)


class BaseExceptionCeleryAppError(Exception):
    """Base exception class for Celery app errors."""


class BotNotFoundError(AttributeError):
    """Exceção para indicar que o robô especificado não foi encontrado.

    Args:
        message (str): Mensagem de erro.

    Returns:
        None

    Raises:
        AttributeError: Sempre que o robô não for localizado.

    """

    def __init__(
        self,
        message: str,
        name: str | None = None,
        obj: object | None = None,
    ) -> None:
        """Inicializa a exceção BotNotFoundError.

        Args:
            message (str): Mensagem de erro.
            name (str | None): Nome do robô, se disponível.
            obj (object | None): Objeto relacionado ao erro, se disponível.



        """
        self.name = name
        self.obj = obj
        super().__init__(message)


class ExecutionError(BaseCrawJUDError):
    """Exceção para erros de execução do robô."""

    def __init__(
        self,
        message: str = MessageError,
        exc: Exception | None = None,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message + formata_msg(exc)

        if message == "Erro ao executar operaçao: " and exc:
            self.message = message + "\n".join(traceback.format_exception(exc))

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class LoginSystemError(BaseCrawJUDError):
    """Exceção para erros de login robô."""

    def __init__(
        self,
        message: str = MessageError,
        exc: Exception | None = None,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message + formata_msg(exc)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class ProcNotFoundError(BaseCrawJUDError):
    """Exception de Processo não encontrado."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message

        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class GrauIncorretoError(BaseCrawJUDError):
    """Exception de Grau Incorreto/Não informado."""

    def __init__(
        self,
        exc: Exception,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message + formata_msg(exc)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class SaveError(BaseCrawJUDError):
    """Exception para erros de salvamento de Formulários/Arquivos."""

    def __init__(
        self,
        exc: Exception,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message

        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class FileError(BaseCrawJUDError):
    """Exception para erros de envio de arquivos."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de envio de arquivos."""
        self.message = message

        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class CadastroParteError(BaseCrawJUDError):
    """Exception para erros de cadastro de parte no Elaw."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class MoveNotFoundError(BaseCrawJUDError):
    """Exception para erros de movimentações não encontradas."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class PasswordError(BaseCrawJUDError):
    """Exception para erros de senha."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de senha."""
        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class NotFoundError(BaseCrawJUDError):
    """Exceção para erros de execução do robô."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message

        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class FileUploadError(BaseCrawJUDError):
    """Exception para erros de upload de arquivos."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de upload de arquivos."""
        self.message = message

        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


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


__all__ = [
    "ExecutionError",
    "DriverNotCreatedError",
    "AuthenticationError",
    "BotNotFoundError",
    "BaseCrawJUDError",
    "BaseExceptionCeleryAppError",
]
