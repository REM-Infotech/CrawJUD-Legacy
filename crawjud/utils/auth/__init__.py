"""Módulo utiliário de autenticação nos sistemas."""

from __future__ import annotations

from .elaw import ElawAuth
from .esaj import EsajAuth
from .pje import PjeAuth
from .projudi import ProjudiAuth

__all__ = ["ElawAuth", "EsajAuth", "PjeAuth", "ProjudiAuth"]
