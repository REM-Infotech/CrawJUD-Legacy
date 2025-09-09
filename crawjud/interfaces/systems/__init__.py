"""Tipos relacionados a sistemas externos."""

from __future__ import annotations

from .pje import *  # noqa: F403, F401
from .webdriver import *  # noqa: F403, F401

__all__ = [
    # PJe types are re-exported from pje module
    # WebDriver types are re-exported from webdriver module
]