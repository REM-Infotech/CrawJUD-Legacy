"""Modulo de controle da model bots."""

from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped

from app.resources.extensions import db

if TYPE_CHECKING:
    from app.models._users import LicenseUser, User

rel = db.relationship


class Bots(db.Model):
    __tablename__ = "bots"
    Id: int = Column("id", Integer, primary_key=True)
    display_name: str = Column(String(64), nullable=False)
    sistema: str = Column(String(16), nullable=False)
    categoria: str = Column(String(32), nullable=False)
    configuracao_form: str = Column(
        String(64), nullable=False, default=""
    )
    descricao: str = Column(
        "descricao", String(length=256), nullable=False
    )

    license_id: int = Column(Integer, db.ForeignKey("licenses.id"))
    license_: Mapped[LicenseUser] = rel(back_populates="bots")

    executions: Mapped[list[ExecucoesBot]] = rel(back_populates="bot")


class ExecucoesBot(db.Model):
    """Model de execuções dos bots."""

    __tablename__ = "executions"
    Id: int = Column("id", Integer, primary_key=True)
    pid: str = Column(String(length=64), nullable=False)
    status: str = Column("status", String(length=64), nullable=False)

    user_id: int = Column(Integer, db.ForeignKey("users.id"))
    usuario: Mapped[User] = rel(back_populates="execucoes")

    bot_id: int = Column(Integer, db.ForeignKey("bots.id"))
    bot: Mapped[Bots] = rel(back_populates="executions")


class CredenciaisRobo(db.Model):
    """Credenciais Bots Model."""

    __tablename__ = "credenciais_robo"
    Id: int = Column("id", Integer, primary_key=True)
    nome_credencial: str = Column(
        "nome_credencial", String(length=64), nullable=False
    )
    sistema: str = Column("sistema", String(length=64), nullable=False)
    login: str = Column("login", String(length=64))
    password: str = Column("senha", String(length=64), nullable=False)

    license_id: int = Column(Integer, db.ForeignKey("licenses.id"))
    license_: Mapped[LicenseUser] = rel(back_populates="credenciais")
