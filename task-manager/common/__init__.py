"""Fornece funcionalidades comuns para o aplicativo CrawJUD."""

from ._raises import raise_execution_error as raise_execution_error
from ._raises import raise_password_token

__all__ = ["raise_execution_error", "raise_password_token"]
