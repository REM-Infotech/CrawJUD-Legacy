"""Module for configuration routes.

This module aggregates the blueprints for admin, supersu, and user configurations.
"""

from crawjud_bots.web.routes.config.admin import admin
from crawjud_bots.web.routes.config.superSu import supersu
from crawjud_bots.web.routes.config.user import usr

__all__ = [usr, admin, supersu]
