"""Módulo de gestão de Models do banco de dados."""

from __future__ import annotations

from typing import TypedDict

from flask import Flask

from app.models.users import LicenseUser, User
from app.resources.extensions import db

__all__ = [
    "LicenseUser",
    "User",
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

        usr_check = db.session.query(User)
        usr_check = usr_check.filter_by(login=cfg["ROOT_USERNAME"])
        usr_check = usr_check.first()

        if not usr_check:
            to_add = []
            root_user = User(
                login=cfg["ROOT_USERNAME"],
                password=cfg["ROOT_PASSWORD"],
                email=cfg["ROOT_EMAIL"],
                client=cfg["ROOT_CLIENT"],
                cpf_cnpj_client=cfg["ROOT_CPF_CNPJ_CLIENT"],
            )
            lic = db.session.query(LicenseUser)
            lic = lic.filter_by(desc="Root License")
            lic = lic.first()

            to_add.append(root_user)

            if lic:
                root_license = LicenseUser(desc="Root License")
                root_user.license_id = root_license.Id

                to_add.append(root_license)

            db.session.add_all(to_add)
            db.session.commit()
