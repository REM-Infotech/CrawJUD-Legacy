from typing import NoReturn

from .exceptions import ExecutionError, PasswordTokenError


def raise_password_token() -> NoReturn:
    """Password token error.

    Raises:
        PasswordTokenError: PasswordTokenError

    """
    raise PasswordTokenError(message="Senha Incorreta!")


def raise_execution_error(message: str) -> NoReturn:
    raise ExecutionError(message=message)
