"""Fornece funcionalidades comuns para o aplicativo CrawJUD."""

from ._raises import auth_error, raise_execution_error, raise_password_token

__all__ = ["auth_error", "raise_execution_error", "raise_password_token"]
