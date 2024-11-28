from typing import Union

from .busca_pags import busca_pags
from .capa import capa
from .emissao import emissao
from .movimentacao import movimentacao
from .protocolo import protocolo

Hints = Union[capa, protocolo, busca_pags, emissao, movimentacao]


class esaj:

    bots = {
        "capa": capa,
        "protocolo": protocolo,
        "busca_pags": busca_pags,
        "emissao": emissao,
        "movimentacao": movimentacao,
    }

    def __init__(self, **kwrgs):
        self.kwrgs = kwrgs
        self.__dict__.update(kwrgs)
        try:

            self.Bot.execution()

        except Exception as e:
            raise e

    @property
    def Bot(self) -> Hints:

        rb = self.bots.get(self.typebot)
        if not rb:
            raise AttributeError("Robô não encontrado!!")

        return rb(**self.kwrgs)
