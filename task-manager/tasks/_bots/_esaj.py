from bots.esaj.capa import Capa as EsajCapa
from bots.esaj.emissao import Emissao as EsajEmissao
from bots.esaj.movimentacao import Movimentacao as EsajMovimentacao
from bots.esaj.protocolo import Protocolo as EsajProtocolo
from celery import shared_task


@shared_task(name="esaj.capa", bind=True, base=EsajCapa)
def esaj_capa(self: EsajCapa) -> None:
    self.execution()


@shared_task(name="esaj.movimentacao", bind=True, base=EsajMovimentacao)
def esaj_movimentacao(self: EsajMovimentacao) -> None:
    self.execution()


@shared_task(name="esaj.protocolo", bind=True, base=EsajProtocolo)
def esaj_protocolo(self: EsajProtocolo) -> None:
    self.execution()


@shared_task(name="esaj.emissao", bind=True, base=EsajEmissao)
def esaj_emissao(self: EsajEmissao) -> None:
    self.execution()
