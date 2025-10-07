from typing import cast

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped  # noqa: F401

from app.config.extensions import db

from .license import License


class User(db.Model):
    __tablename__ = "users"
    Id = Column("id", Integer, primary_key=True, nullable=False, unique=True)
    UserName = Column("username", String(128), nullable=False)
    DisplayName = Column("display_name", String(128), nullable=False)
    Email = Column("email", String(64), nullable=False)

    license_id = Column(
        "license_id", Integer, db.ForeignKey("licenses.id"), nullable=False
    )
    License: Mapped["License"] = cast(Mapped["License"], db.relationship())
