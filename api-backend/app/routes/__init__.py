"""Module for main application routes.

This module defines global routes, context processors, and custom error handling.
"""

from __future__ import annotations

from . import _bots, _root, handlers

__all__ = ["_bots", "_root", "handlers"]


def register_routes(*args) -> None: ...
