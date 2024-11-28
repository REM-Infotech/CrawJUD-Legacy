import logging
from typing import Union

from clear import clear

from .capa import capa
from .movimentacao import movimentacao
from .proc_parte import proc_parte
from .protocolo import protocolo

Hints = Union[capa, protocolo, proc_parte, movimentacao]


class projudi:

    bots = {
        "capa": capa,
        "protocolo": protocolo,
        "proc_parte": proc_parte,
        "movimentacao": movimentacao,
    }

    def __init__(self, **kwrgs):
        self.kwrgs = kwrgs
        self.__dict__.update(kwrgs)
        try:

            self.Bot.execution()

        except Exception as e:
            clear()
            logging.error(f"Exception: {e}", exc_info=True)

    @property
    def Bot(self) -> Hints:

        rb = self.bots.get(self.typebot)
        if not rb:
            raise AttributeError("Robô não encontrado!!")

        return rb(**self.kwrgs)
