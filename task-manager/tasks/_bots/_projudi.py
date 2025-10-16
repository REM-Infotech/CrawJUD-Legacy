from bots.projudi.capa import Capa as ProjudiCapa
from bots.projudi.intimacoes import Intimacoes as ProjudiIntimacoes
from bots.projudi.movimentacao import Movimentacao as ProjudiMovimentacao
from bots.projudi.proc_parte import ProcParte as ProjudiProcParte
from bots.projudi.protocolo import Protocolo as ProjudiProtocolo
from celery import shared_task


@shared_task(name="projudi.capa", bind=True, base=ProjudiCapa)
def projudi_capa(self: ProjudiCapa) -> None:
    self.execution()


@shared_task(name="projudi.movimentacao", bind=True, base=ProjudiMovimentacao)
def projudi_movimentacao(self: ProjudiMovimentacao) -> None:
    self.execution()


@shared_task(name="projudi.intimacoes", bind=True, base=ProjudiIntimacoes)
def projudi_intimacoes(self: ProjudiIntimacoes) -> None:
    self.execution()


@shared_task(name="projudi.protocolo", bind=True, base=ProjudiProtocolo)
def projudi_protocolo(self: ProjudiProtocolo) -> None:
    self.execution()


@shared_task(name="projudi.proc_parte", bind=True, base=ProjudiProcParte)
def projudi_proc_parte(self: ProjudiProcParte) -> None:
    self.execution()
