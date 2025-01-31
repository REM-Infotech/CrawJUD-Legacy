"""
Module: caixa.

This module initializes and manages the Caixa bot within the CrawJUD-Bots application.
"""

import logging
import traceback
from importlib import import_module
from typing import Any

from ...common import StartError


class caixa:
    """
    caixa class.

    Initializes and executes the Caixa bot based on provided configurations.
    """

    def __init__(self, **kwrgs) -> None:
        """
        Initialize a new caixa instance.

        Args:
            **kwrgs: Variable keyword arguments for bot configuration.

        Raises:
            StartError: If an exception occurs during bot execution.
        """
        self.kwrgs = kwrgs
        self.__dict__.update(kwrgs)
        try:
            self.Bot.execution()

        except Exception as e:
            logging.error(f"Exception: {e}", exc_info=True)
            raise StartError(traceback.format_exc())

    @property
    def Bot(self) -> Any:
        """
        Bot property.

        Dynamically imports and returns an instance of the specified bot type.

        Returns:
            Any: An instance of the specified bot.

        Raises:
            AttributeError: If the specified bot type is not found.
        """
        rb = getattr(
            import_module(f".{self.typebot.lower()}", __package__),
            self.typebot.lower(),
        )

        # rb = self.bots.get(self.typebot)
        if not rb:
            raise AttributeError("Robô não encontrado!!")

        return rb(**self.kwrgs)
