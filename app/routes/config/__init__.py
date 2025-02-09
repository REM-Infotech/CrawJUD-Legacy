"""Module for configuration routes.

This module aggregates the blueprints for admin, supersu, and user configurations.
"""

from app.routes.config.admin import admin
from app.routes.config.superSu import supersu
from app.routes.config.user import usr

__all__ = [usr, admin, supersu]
