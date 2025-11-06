from __future__ import annotations

import re
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped

from app import crypt_context
from app.resources.extensions import db

from ._bot import Bots, CredenciaisRobo

if TYPE_CHECKING:
    from app.models._bot import ExecucoesBot


rel = db.relationship


def _generate_key() -> str:
    return re.sub(
        r"(.{8})(.{8})(.{8})(.{8})",
        r"\1-\2-\3-\4",
        uuid4().hex,
    ).upper()


class LicenseUser(db.Model):
    __tablename__ = "licenses"
    Id: int = Column("id", Integer, primary_key=True, nullable=False)
    ProductKey: str = Column(
        "product_key",
        String(35),
        default=_generate_key,
    )
    descricao: int = Column(
        "descricao",
        String(length=256),
        nullable=False,
    )
    Nome: str = Column("nome", String(64))

    CPF: str = Column(
        "cpf",
        String(14),
        nullable=False,
        default="000.000.000-00",
    )
    CNPJ: str = Column(
        "cnpj",
        String(18),
        nullable=False,
        default="00.000.000/0000-00",
    )

    bots: Mapped[list[Bots]] = rel(back_populates="license_")
    usuarios: Mapped[list[User]] = rel(back_populates="license_")
    credenciais: Mapped[list[CredenciaisRobo]] = rel(
        back_populates="license_",
    )


class User(db.Model):
    __tablename__ = "users"
    Id: int = Column("id", Integer, primary_key=True)
    login: str = Column(
        "username",
        String(length=30),
        nullable=False,
        unique=True,
    )
    nome_usuario: str = Column(
        "display_name",
        String(length=64),
        nullable=False,
    )
    email: str = Column(
        "email",
        String(length=50),
        nullable=False,
        unique=True,
    )
    password: str = Column(
        "password",
        String(length=64),
        nullable=False,
    )
    admin: bool = Column("admin", Boolean, default=False)

    execucoes: Mapped[list[ExecucoesBot]] = rel(
        back_populates="usuario",
    )

    license_id: int = Column(Integer, ForeignKey("licenses.id"))
    license_: Mapped[LicenseUser] = rel(back_populates="usuarios")

    @classmethod
    def authenticate(cls, username: str, password: str) -> bool:
        user = (
            db.session.query(cls).filter(cls.login == username).first()
        )
        return user is not None and user.check_password(password)

    @property
    def senhacrip(self) -> str:
        return self.senhacrip

    @senhacrip.setter
    def senhacrip(self, senha_texto: str) -> None:
        self.password = crypt_context.hash(senha_texto)

    def check_password(self, senha_texto_claro: str) -> bool:
        valid_hash = crypt_context.verify(
            senha_texto_claro,
            self.password,
            scheme="argon2",
        )

        if valid_hash:
            if crypt_context.needs_update(self.password):
                self.password = crypt_context.hash(senha_texto_claro)
                db.session.add(self)
                db.session.commit()

            return True

        return False
