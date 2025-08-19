"""Pacote público para funcionalidades do PJeBot."""

from __future__ import annotations

import importlib

capa = importlib.import_module(".capa", __package__)

__all__ = ["capa"]
