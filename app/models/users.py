"""Database models for users and related entities in CrawJUD-Bots."""

from datetime import datetime
from uuid import uuid4

import bcrypt
import pytz

from app import db

salt = bcrypt.gensalt()


class SuperUser(db.Model):
    """Represents a superuser linked to a regular user."""

    __tablename__ = "superuser"
    id: int = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    users = db.relationship("Users", backref=db.backref("supersu", lazy=True))


class Users(db.Model):
    """Represents a user in the CrawJUD-Bots application."""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(length=30), nullable=False, unique=True)
    nome_usuario = db.Column(db.String(length=64), nullable=False, unique=True)
    email = db.Column(db.String(length=50), nullable=False, unique=True)
    password = db.Column(db.String(length=60), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.now(pytz.timezone("America/Manaus")))
    verification_code = db.Column(db.String(length=45), unique=True)
    login_id = db.Column(db.String(length=64), nullable=False, default=str(uuid4()))
    filename = db.Column(db.String(length=128))
    blob_doc = db.Column(db.LargeBinary(length=(2**32) - 1))

    licenseus_id = db.Column(db.Integer, db.ForeignKey("licenses_users.id"))
    licenseusr = db.relationship("LicensesUsers", backref="user")

    @property
    def senhacrip(self) -> None:
        """Get the hashed password."""
        return self.senhacrip

    @senhacrip.setter
    def senhacrip(self, senha_texto: str) -> None:
        """Set the hashed password from plaintext.

        Args:
            senha_texto (str): The plaintext password.

        """
        self.password = bcrypt.hashpw(senha_texto.encode(), salt).decode("utf-8")

    def check_password(self, senha_texto_claro: str) -> bool:
        """Verify the plaintext password against the hashed password.

        Args:
            senha_texto_claro (str): The plaintext password.

        Returns:
            bool: True if passwords match, False otherwise.

        """
        return bcrypt.checkpw(senha_texto_claro.encode("utf-8"), self.password.encode("utf-8"))


class LicensesUsers(db.Model):
    """Represents a license user in the CrawJUD-Bots application."""

    __tablename__ = "licenses_users"
    id: int = db.Column(db.Integer, primary_key=True)
    name_client: str = db.Column(db.String(length=60), nullable=False, unique=True)
    cpf_cnpj: str = db.Column(db.String(length=30), nullable=False, unique=True)
    license_token: str = db.Column(db.String(length=512), nullable=False, unique=True)

    # Relacionamento de muitos para muitos com users
    admins = db.relationship("Users", secondary="admins", backref="admin")
    bots = db.relationship("BotsCrawJUD", secondary="execution_bots", backref=db.backref("license", lazy=True))
