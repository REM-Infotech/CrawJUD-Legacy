from bots.pje.capa import Capa as PjeCapa
from celery import shared_task


@shared_task(name="pje.capa", bind=True, base=PjeCapa)
def pje_capa(self: PjeCapa) -> None:
    self.execution()
