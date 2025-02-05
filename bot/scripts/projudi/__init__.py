"""Module: projudi.

This module defines the projudi class, which manages the initialization and execution
of different bot types within the CrawJUD-Bots application.
"""

from __future__ import annotations

import logging
import traceback
from importlib import import_module
from typing import Union

from ...common.exceptions import StartError

logger = logging.getLogger(__name__)


class projudi:  # noqa: N801
    """The projudi class initializes and executes the specified bot based on provided configurations.

    Attributes:
        kwrgs (dict): Keyword arguments containing configuration parameters for the bot.

    """

    def __init__(self, **kwrgs: dict) -> None:
        """Initialize the projudi instance with the given keyword arguments.

        Args:
            **kwrgs: Arbitrary keyword arguments for bot configuration.

        Raises:
            StartError: If an exception occurs during bot execution.

        """
        self.kwrgs = kwrgs
        self.__dict__.update(kwrgs)
        try:
            self.Bot.execution()

        except Exception as e:
            err = traceback.format_exc()
            logger.exception(err)

            raise StartError(traceback.format_exc()) from e

    @property
    def Bot(self) -> ClassBots:  # noqa: N802
        """Get the bot instance based on the 'typebot' configuration.

        Returns:
            ClassBots: An instance of the specified bot class.

        Raises:
            AttributeError: If the specified bot type is not found.

        """
        module_rb = import_module(f".{self.typebot.lower()}", __package__)
        rb: ClassBots = getattr(module_rb, self.typebot.lower())

        # rb = self.bots.get(self.typebot)
        if not rb:
            raise AttributeError("Robô não encontrado!!")

        return rb(**self.kwrgs)


if __name__ == "__main__":
    from .capa import capa
    from .movimentacao import movimentacao
    from .proc_parte import proc_parte
    from .protocolo import protocolo

    ClassBots = Union[proc_parte, capa, movimentacao, protocolo]
