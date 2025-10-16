"""Pacote de bots PJe."""

from celery import shared_task

from bots.pje.capa import Capa as PjeCapa


@shared_task(name="pje.capa", bind=True, base=PjeCapa)
def pje_capa(self: PjeCapa) -> None:
    """Task PJe Capa."""
    self.execution()
