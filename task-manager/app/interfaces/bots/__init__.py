"""Tipos relacionados aos bots do CrawJUD."""

from __future__ import annotations

from .data import BotData, DictFiles, DictReturnAuth, PolosProcessuais
from .pje import DictDesafio, DictResults, DictSeparaRegiao, Resultados

__all__ = [
    # Bot data
    "BotData",
    "DictFiles",
    "DictReturnAuth",
    "PolosProcessuais",
    # PJe bot types
    "DictDesafio",
    "DictResults",
    "DictSeparaRegiao",
    "Resultados",
]
