"""Module for configuration routes.

This module aggregates the blueprints for admin, supersu, and user configurations.
"""

from crawjud.routes.config.admin import admin
from crawjud.routes.config.superSu import supersu
from crawjud.routes.config.user import usr

__all__ = [usr, admin, supersu]
