"""Fornece funcionalidades comuns para o aplicativo CrawJUD."""

from ._raises import raise_execution_error as _raise_execution_error
from ._raises import raise_password_token

__all__ = ["_raise_execution_error", "raise_password_token"]
