"""Módulo utilitário de busca."""

from __future__ import annotations

from .elaw import ElawSearch
from .esaj import EsajSearch
from .projudi import ProjudiSearch

__all__ = ["ElawSearch", "EsajSearch", "ProjudiSearch"]
