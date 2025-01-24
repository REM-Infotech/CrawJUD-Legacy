import logging
import traceback
from importlib import import_module
from typing import Any

from ...common import StartError


class caixa:

    def __init__(self, **kwrgs) -> None:
        self.kwrgs = kwrgs
        self.__dict__.update(kwrgs)
        try:

            self.Bot.execution()

        except Exception as e:

            logging.error(f"Exception: {e}", exc_info=True)
            raise StartError(traceback.format_exc())

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
