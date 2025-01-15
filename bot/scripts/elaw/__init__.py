from importlib import import_module
from typing import Any

# from .andamentos import andamentos
# from .prazos import prazos
# from .cadastro import cadastro
# from .complementar import complement
# from .download import download
# from .pagamentos import sol_pags
# from .provisionamento import provisao

# Hints = Union[download, cadastro, sol_pags, andamentos, complement, provisao, prazos]


class elaw:

    # bots = {
    #     "download": download,
    #     "cadastro": cadastro,
    #     "sol_pags": sol_pags,
    #     "andamentos": andamentos,
    #     "complement": complement,
    #     "provisao": provisao,
    #     "prazos": prazos,
    # }

    def __init__(self, **kwrgs) -> None:
        self.kwrgs = kwrgs
        self.__dict__.update(kwrgs)
        try:

            self.Bot.execution()

        except Exception as e:
            raise e

    @property
    def Bot(self) -> Any:

        rb = getattr(
            import_module(f".{self.typebot.lower()}", __package__),
            self.typebot.lower(),
        )

        # rb = self.bots.get(self.typebot)
        if not rb:
            raise AttributeError("Robô não encontrado!!")

        return rb(**self.kwrgs)
