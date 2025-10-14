from __future__ import annotations

import bcrypt
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped

from app.resources.extensions import db

from ._bot import Bots

salt = bcrypt.gensalt()


class LicenseUser(db.Model):
    """Modelo de controle da tabela license."""

    __tablename__ = "licenses"
    Id: int = Column("id", Integer, primary_key=True, nullable=False)
    desc: int = Column("description", String(length=256), nullable=False)
    Bot_Id: int = Column(
        "bot_id",
        Integer,
        ForeignKey("bots.id"),
        nullable=False,
    )
    Bots: Mapped[Bots] = db.relationship()


class User(db.Model):
    """Model para controle da tabela users."""

    __tablename__ = "users"
    id: int = Column(Integer, primary_key=True)
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
    password: str = Column("password", String(length=64), nullable=False)

    license_id: int = Column(Integer, ForeignKey("licenses.id"))
    License: Mapped[LicenseUser] = db.relationship()

    admin: bool = Column("admin", Boolean, default=False)

    @classmethod
    def authenticate(cls, username: str, password: str) -> bool:
        """Autenticação do usuário.

        Arguments:
            username (str): Nome de usuário.
            password (str): Senha do usuário.

        Returns:
            bool: True se autenticado, False caso contrário.

        """
        user = db.session.query(cls).filter(cls.login == username).first()
        return user is not None and user.check_password(password)

    @property
    def senhacrip(self) -> str:
        """Get the encrypted password.

        Returns:
            str: The encrypted password.

        """
        return self.senhacrip

    @senhacrip.setter
    def senhacrip(self, senha_texto: str) -> None:
        """Encrypt and set the user password.

        Args:
            senha_texto (str): Plain text password.

        """
        self.password = bcrypt.hashpw(senha_texto.encode(), salt).decode(
            "utf-8",
        )

    def check_password(self, senha_texto_claro: str) -> bool:
        """Check if the provided password matches the stored encrypted password.

        Args:
            senha_texto_claro (str): Plain text password.

        Returns:
            bool: True if valid, False otherwise.

        """
        return bcrypt.checkpw(
            senha_texto_claro.encode("utf-8"),
            self.password.encode("utf-8"),
        )
