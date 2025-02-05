"""Module: elaw.

This module initializes and manages the elaw bots within the CrawJUD-Bots application.
"""

import logging
import traceback
from importlib import import_module
from typing import Any

from ...common import StartError


class Elaw:
    """The Elaw class manages the initialization and execution of elaw bots.

    Attributes:
        kwrgs (dict): Keyword arguments for bot configuration.

    """

    def __init__(self, **kwrgs) -> None:
        """Initialize the Elaw instance.

        This method updates the instance's dictionary with the provided keyword arguments
        and executes the bot. Errors during execution are logged and raised as StartError.

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
            logging.exception(err)

            raise StartError(traceback.format_exc()) from e

    @property
    def Bot(self) -> Any:  # noqa: N802
        """Retrieve the bot instance based on the typebot attribute.

        Returns:
            Any: An instance of the specified bot class.

        Raises:
            AttributeError: If the specified bot is not found.

        """
        bot_class = getattr(import_module(f".{self.typebot.lower()}", __package__), self.typebot.lower())

        if not bot_class:
            raise AttributeError("Robô não encontrado!!")

        return bot_class(**self.kwrgs)
