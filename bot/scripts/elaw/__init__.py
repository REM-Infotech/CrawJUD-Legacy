from typing import Union

from .andamentos import andamentos
from .audiencia import audiencia as prazos
from .cadastro import cadastro
from .complementar import complement
from .download import download
from .pagamentos import sol_pags
from .provisionamento import provisao

Hints = Union[download, cadastro, sol_pags, andamentos, complement, provisao, prazos]


class elaw:

    bots = {
        "download": download,
        "cadastro": cadastro,
        "sol_pags": sol_pags,
        "andamentos": andamentos,
        "complement": complement,
        "provisao": provisao,
        "prazos": prazos,
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
