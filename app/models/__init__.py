"""Módulo de gestão de Models do banco de dados."""

from __future__ import annotations

from typing import TypedDict

from dotenv import dotenv_values
from flask import current_app as app

from app.models.users import LicenseUser, User
from app.resources.extensions import db

__all__ = [
    "LicenseUser",
    "User",
]

environ = dotenv_values()


class DatabaseInitEnvDict(TypedDict):
    ROOT_USERNAME: str
    ROOT_PASSWORD: str
    ROOT_EMAIL: str
    ROOT_CLIENT: str
    ROOT_CPF_CNPJ_CLIENT: str


def init_database() -> None:
    """Inicializa o banco de dados."""
    with app.app_context():
        db.create_all()
