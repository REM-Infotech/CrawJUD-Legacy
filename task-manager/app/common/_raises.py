from typing import NoReturn

from app.common.exceptions.validacao import ValidacaoStringError

from .exceptions import ExecutionError, PasswordTokenError


def raise_password_token() -> NoReturn:
    """Password token error.

    Raises:
        PasswordTokenError: PasswordTokenError

    """
    raise PasswordTokenError(message="Senha Incorreta!")


def raise_execution_error(message: str) -> NoReturn:
    raise ExecutionError(message=message)


def auth_error() -> NoReturn:
    raise ExecutionError(message="Erro de autenticacao")


def value_error() -> NoReturn:
    raise ValidacaoStringError(
        message="Valor informado não corresponde ao valor esperado",
    )
