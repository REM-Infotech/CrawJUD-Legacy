"""Módulo de modelos do SQLAlchemy de administração."""

from .license import License
from .user import User

__all__ = ["User", "License"]
