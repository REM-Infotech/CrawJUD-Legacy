from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped

from app import crypt_context
from app.resources.extensions import db

from ._bot import Bots


class LicenseUser(db.Model):
    __tablename__ = "licenses"
    Id: int = Column("id", Integer, primary_key=True, nullable=False)
    desc: int = Column("description", String(length=256), nullable=False)
    Bot_Id: int = Column("bot_id", Integer, ForeignKey("bots.id"))
    Bots: Mapped[Bots] = db.relationship()


class User(db.Model):
    __tablename__ = "users"
    id: int = Column(Integer, primary_key=True)
    login: str = Column(
        "username", String(length=30), nullable=False, unique=True
    )
    nome_usuario: str = Column(
        "display_name", String(length=64), nullable=False
    )
    email: str = Column("email", String(length=50), nullable=False, unique=True)
    password: str = Column("password", String(length=64), nullable=False)

    license_id: int = Column(Integer, ForeignKey("licenses.id"))
    License: Mapped[LicenseUser] = db.relationship()

    admin: bool = Column("admin", Boolean, default=False)

    @classmethod
    def authenticate(cls, username: str, password: str) -> bool:
        user = db.session.query(cls).filter(cls.login == username).first()
        return user is not None and user.check_password(password)

    @property
    def senhacrip(self) -> str:
        return self.senhacrip

    @senhacrip.setter
    def senhacrip(self, senha_texto: str) -> None:
        self.password = crypt_context.hash(senha_texto)

    def check_password(self, senha_texto_claro: str) -> bool:
        valid_hash = crypt_context.verify(
            senha_texto_claro, self.password, scheme="argon2"
        )

        if valid_hash:
            if crypt_context.needs_update(self.password):
                self.password = crypt_context.hash(senha_texto_claro)
                db.session.add(self)
                db.session.commit()

            return True

        return False
