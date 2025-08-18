"""Module: projudi.

Manage initialization and execution of various Projudi bot types within CrawJUD-Bots.
"""

from __future__ import annotations

from crawjud.bots.projudi.capa import Capa
from crawjud.bots.projudi.intimacoes import Intimacoes
from crawjud.bots.projudi.movimentacao import Movimentacao
from crawjud.bots.projudi.proc_parte import ProcParte
from crawjud.bots.projudi.protocolo import Protocolo

__all__ = [
    "Capa",
    "Intimacoes",
    "Movimentacao",
    "ProcParte",
    "Protocolo",
]
