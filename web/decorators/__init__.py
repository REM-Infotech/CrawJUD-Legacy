"""Module for importing and managing decorators in the application."""

from .checks import check_privilegies
from .login_wrap import login_required

__all__ = ["check_privilegies", "login_required"]
