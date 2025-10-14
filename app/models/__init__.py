"""Módulo de gestão de Models do banco de dados."""

from __future__ import annotations

from typing import TypedDict

from flask import Flask

from app.models.users import LicenseUser, User
from app.resources.extensions import db

from ._jwt import TokenBlocklist

__all__ = [
    "LicenseUser",
    "User",
    "TokenBlocklist",
]


class DatabaseInitEnvDict(TypedDict):
    ROOT_USERNAME: str
    ROOT_PASSWORD: str
    ROOT_EMAIL: str
    ROOT_CLIENT: str
    ROOT_CPF_CNPJ_CLIENT: str


def init_database(app: Flask) -> None:
    """Inicializa o banco de dados."""
    with app.app_context(), db.session.no_autoflush:
        db.create_all()
        cfg = app.config

        user = (
            db.session.query(User)
            .filter_by(login=cfg["ROOT_USERNAME"])
            .first()
        )

        if not user:
            data = {
                "login": cfg["ROOT_USERNAME"],
                "password": cfg["ROOT_PASSWORD"],
                "email": cfg["ROOT_EMAIL"],
                "nome_usuario": "Root User",
            }
            root_user = User(**data)
            root_license = (
                db.session.query(LicenseUser)
                .filter_by(desc="Root License")
                .first()
            )

            if not root_license:
                root_license = LicenseUser(desc="Root License")

            root_user.license_id = root_license.Id
            db.session.add_all([root_license, root_user])
            db.session.commit()
