from __future__ import annotations
import logging
import traceback
from importlib import import_module
from typing import Union

from ...common.exceptions import StartError


class projudi:

    def __init__(self, **kwrgs) -> None:
        self.kwrgs = kwrgs
        self.__dict__.update(kwrgs)
        try:

            self.Bot.execution()

        except Exception as e:

            logging.error(f"Exception: {e}", exc_info=True)
            raise StartError(traceback.format_exc())

    @property
    def Bot(self) -> ClassBots:

        module_rb = import_module(f".{self.typebot.lower()}", __package__)
        rb: ClassBots = getattr(
            module_rb,
            self.typebot.lower(),
        )

        # rb = self.bots.get(self.typebot)
        if not rb:
            raise AttributeError("Robô não encontrado!!")

        return rb(**self.kwrgs)


if __name__ == "__main__":
    from .proc_parte import proc_parte
    from .capa import capa
    from .movimentacao import movimentacao
    from .protocolo import protocolo

    ClassBots = Union[proc_parte, capa, movimentacao, protocolo]
