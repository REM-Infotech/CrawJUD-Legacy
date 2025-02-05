"""
Module: calculadoras.

This module initializes and manages the Calculadoras bot within the CrawJUD-Bots application.
"""

import logging
import traceback
from importlib import import_module
from typing import Any

from ...common import StartError


class calculadoras:  # noqa: N801
    """
    calculadoras class.

    Initializes and executes the Calculadoras bot based on provided configurations.
    """

    def __init__(self, **kwrgs) -> None:
        """
        Initialize a new calculadoras instance.

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
            logging.exception(err)

            raise StartError(traceback.format_exc()) from e

    @property
    def Bot(self) -> Any:  # noqa: N802
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
