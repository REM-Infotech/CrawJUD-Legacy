"""Pacote de bots Projudi."""

from bots.projudi.capa import Capa as ProjudiCapa
from bots.projudi.intimacoes import Intimacoes as ProjudiIntimacoes
from bots.projudi.movimentacao import Movimentacao as ProjudiMovimentacao
from bots.projudi.proc_parte import ProcParte as ProjudiProcParte
from bots.projudi.protocolo import Protocolo as ProjudiProtocolo

__all__ = [
    "ProjudiCapa",
    "ProjudiIntimacoes",
    "ProjudiMovimentacao",
    "ProjudiProcParte",
    "ProjudiProtocolo",
]
