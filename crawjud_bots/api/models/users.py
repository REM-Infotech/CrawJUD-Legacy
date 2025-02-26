"""Defines the database models for user management in CrawJUD-Bots.

It includes models for superuser links, user credentials, and license associations.

"""

from datetime import datetime
from uuid import uuid4

import bcrypt
import pytz

from crawjud_bots.api import db

salt = bcrypt.gensalt()


class SuperUser(db.Model):
    """Represents a superuser, linked to a regular user.

    Attributes:
        id (int): Primary key for the superuser.
        users_id (int): Foreign key referencing a user record.
        users (Users): Relationship to the associated user model.

    """

    __tablename__ = "superuser"
    id: int = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    users = db.relationship("Users", backref=db.backref("supersu", lazy=True))


class Users(db.Model):
    """Defines a user entity in the CrawJUD-Bots system.

    Attributes:
        id (int): Primary key for the user.
        login (str): Username or login identifier.
        nome_usuario (str): Display name for the user.
        email (str): Email address of the user.
        password (str): Hashed user password.
        login_time (datetime): Last login time with default to Manaus timezone.
        verification_code (str): Code used for user verification.
        login_id (str): Unique login session identifier.
        filename (str): Name of an associated file resource.
        blob_doc (bytes): Binary large object storing user file data.
        licenseus_id (int): Foreign key referencing LicensesUsers.
        licenseusr (LicensesUsers): Relationship for user license data.

    """

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
        """Retrieve the stored hashed password."""
        return self.senhacrip

    @senhacrip.setter
    def senhacrip(self, senha_texto: str) -> None:
        """Hash and store a plaintext password.

        Args:
            senha_texto (str): The plaintext password.

        """
        self.password = bcrypt.hashpw(senha_texto.encode(), salt).decode("utf-8")

    def check_password(self, senha_texto_claro: str) -> bool:
        """Check if a given plaintext password matches the stored hash.

        Args:
            senha_texto_claro (str): The plaintext password for comparison.

        Returns:
            bool: True if the plaintext password matches, otherwise False.

        """
        return bcrypt.checkpw(senha_texto_claro.encode("utf-8"), self.password.encode("utf-8"))


class LicensesUsers(db.Model):
    """Stores license-related data for users.

    Attributes:
        id (int): Primary key for the license user entry.
        name_client (str): Name of the client holding the license.
        cpf_cnpj (str): Unique CPF/CNPJ identifier for the client.
        license_token (str): Token identifying and validating the license.

    """

    __tablename__ = "licenses_users"
    id: int = db.Column(db.Integer, primary_key=True)
    name_client: str = db.Column(db.String(length=60), nullable=False, unique=True)
    cpf_cnpj: str = db.Column(db.String(length=30), nullable=False, unique=True)
    license_token: str = db.Column(db.String(length=512), nullable=False, unique=True)

    # Relacionamento de muitos para muitos com users
    admins = db.relationship("Users", secondary="admins", backref="admin")
    bots = db.relationship("BotsCrawJUD", secondary="execution_bots", backref=db.backref("license", lazy=True))
