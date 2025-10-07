"""Módulo do Modelo User."""

from typing import cast

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.base._sqlalchemy._model import Model
from app.resources.extensions import db

from .license import License


class User(Model):
    """Modelo User."""

    __tablename__ = "users"
    Id: Mapped[int] = mapped_column(
        "id",
        Integer,
        primary_key=True,
        nullable=False,
        unique=True,
    )
    UserName: Mapped[str] = mapped_column(
        "username",
        String(128),
        nullable=False,
    )
    DisplayName: Mapped[str] = mapped_column(
        "display_name",
        String(128),
        nullable=False,
    )
    Email: Mapped[str] = mapped_column("email", String(64), nullable=False)

    license_id: Mapped[int] = mapped_column(
        "license_id",
        Integer,
        db.ForeignKey("licenses.id"),
        nullable=False,
    )
    License: Mapped[License] = cast(Mapped["License"], db.relationship())
