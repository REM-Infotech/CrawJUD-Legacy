import logging
from importlib import import_module

from clear import clear

# from typing import Union


# from .capa import capa
# from .movimentacao import movimentacao
# from .proc_parte import proc_parte
# from .protocolo import protocolo

# Hints = Union[capa, protocolo, proc_parte, movimentacao]


class projudi:

    # bots = {
    #     "capa": capa,
    #     "protocolo": protocolo,
    #     "proc_parte": proc_parte,
    #     "movimentacao": movimentacao,
    # }

    def __init__(self, **kwrgs) -> None:
        self.kwrgs = kwrgs
        self.__dict__.update(kwrgs)
        try:

            self.Bot.execution()

        except Exception as e:
            clear()
            logging.error(f"Exception: {e}", exc_info=True)

    @property
    def Bot(self):

        rb = getattr(
            import_module(f".{self.typebot.lower()}", __package__),
            self.typebot.lower(),
        )

        # rb = self.bots.get(self.typebot)
        if not rb:
            raise AttributeError("Robô não encontrado!!")

        return rb(**self.kwrgs)
