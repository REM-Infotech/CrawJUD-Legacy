"""Módulo de gestão de Models do banco de dados."""

from __future__ import annotations

from flask import Flask

from app.models._users import LicenseUser, User
from app.resources.extensions import db

from ._jwt import TokenBlocklist

__all__ = [
    "LicenseUser",
    "User",
    "TokenBlocklist",
]


def init_database(app: Flask) -> None:
    """Inicializa o banco de dados."""
    with app.app_context(), db.session.no_autoflush:
        db.create_all()

        user = db.session.query(User).filter_by(login=app.config["ROOT_USERNAME"]).first()

        if not user:
            root_user = User(
                login=app.config["ROOT_USERNAME"],
                password=app.config["ROOT_PASSWORD"],
                email=app.config["ROOT_EMAIL"],
                nome_usuario="Root User",
            )

            root_user.admin = True

            root_license = (
                db.session.query(LicenseUser).filter_by(desc="Root License").first()
            )
            if not root_license:
                root_license = LicenseUser(desc="Root License")

            root_user.license_id = root_license.Id
            root_user.License = root_license
            db.session.add_all([root_license, root_user])
            db.session.commit()
