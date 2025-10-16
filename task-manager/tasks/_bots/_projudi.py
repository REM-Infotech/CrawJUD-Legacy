from bots.projudi.capa import Capa as ProjudiCapa
from celery import shared_task


@shared_task(name="projudi.capa", bind=True, base=ProjudiCapa)
def projudi_capa(self: ProjudiCapa) -> None:
    self.execution()
