"""Module for main application routes.

This module defines global routes, context processors, and custom error handling.
"""

from __future__ import annotations

from . import _bots, _root

__all__ = ["_bots", "_root"]


def register_routes(*args) -> None: ...
