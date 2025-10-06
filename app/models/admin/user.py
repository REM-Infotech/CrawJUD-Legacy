from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped  # noqa: F401

from app.config.extensions import db


class User(db.Model):
    __tablename__ = "users"
    Id: int = Column("id", Integer, primary_key=True, nullable=False, unique=True)
    UserName: str = Column("username", String(128), nullable=False)
    DisplayName: str = Column("display_name", String(128), nullable=False)
    Email: str = Column("Email", String(64), nullable=False)
