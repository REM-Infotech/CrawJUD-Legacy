"""Pacote de bots Projudi."""

from celery import shared_task

from __types import AnyType
from __types import Dict as Dict
from bots.projudi.capa import Capa as ProjudiCapa
from bots.projudi.intimacoes import Intimacoes as ProjudiIntimacoes
from bots.projudi.movimentacao import Movimentacao as ProjudiMovimentacao
from bots.projudi.proc_parte import ProcParte as ProjudiProcParte
from bots.projudi.protocolo import Protocolo as ProjudiProtocolo


@shared_task(name="projudi.capa", bind=True, base=ProjudiCapa)
def projudi_capa(self: ProjudiCapa, **kwargs: AnyType) -> None:
    """Task Projudi Capa."""
    self.execution()


@shared_task(name="projudi.movimentacao", bind=True, base=ProjudiMovimentacao)
def projudi_movimentacao(self: ProjudiMovimentacao, **kwargs: AnyType) -> None:
    """Task Projudi Movimentação."""
    self.execution()


@shared_task(name="projudi.intimacoes", bind=True, base=ProjudiIntimacoes)
def projudi_intimacoes(self: ProjudiIntimacoes, **kwargs: AnyType) -> None:
    """Task Projudi Intimações."""
    self.execution()


@shared_task(name="projudi.protocolo", bind=True, base=ProjudiProtocolo)
def projudi_protocolo(self: ProjudiProtocolo, **kwargs: AnyType) -> None:
    """Task Projudi Protocolo."""
    self.execution()


@shared_task(name="projudi.proc_parte", bind=True, base=ProjudiProcParte)
def projudi_proc_parte(self: ProjudiProcParte, **kwargs: AnyType) -> None:
    """Task Projudi ProcParte."""
    self.execution()
