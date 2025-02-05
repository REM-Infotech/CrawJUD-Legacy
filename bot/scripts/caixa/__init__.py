"""Module: caixa.

This module initializes and manages the Caixa bot within the CrawJUD-Bots application.
"""

import logging
import traceback
from importlib import import_module

# from typing import any
from ...common import StartError

logger = logging.getLogger(__name__)


class caixa:  # noqa: N801
    """caixa class.

    Initializes and executes the Caixa bot based on provided configurations.
    """

    def __init__(self, **kwrgs: dict) -> None:
        """Initialize a new caixa instance.

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
            err = traceback.format_exc()
            logger.exception(err)
            raise StartError(traceback.format_exc()) from e

    @property
    def Bot(self) -> any:  # noqa: N802
        """Bot property.

        Dynamically imports and returns an instance of the specified bot type.

        Returns:
            any: An instance of the specified bot.

        Raises:
            AttributeError: If the specified bot type is not found.

        """
        rb = getattr(import_module(f".{self.typebot.lower()}", __package__), self.typebot.lower())

        # rb = self.bots.get(self.typebot)
        if not rb:
            raise AttributeError("Robô não encontrado!!")

        return rb(**self.kwrgs)
