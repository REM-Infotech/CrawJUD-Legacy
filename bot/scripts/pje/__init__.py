"""Provide the pje class to manage and execute the pje Bot."""

from __future__ import annotations

import logging
import traceback
from importlib import import_module

from ...common import StartError

logger = logging.getLogger(__name__)


class pje:  # noqa: N801
    """Represent the pje Bot environment and handle its execution."""

    def __init__(self, **kwrgs: dict) -> None:
        """Initialize the pje instance with the given keyword arguments.

        Raises:
            StartError: If an exception occurs during bot execution

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
        """Return the bot instance configured for this environment.

        Raises:
            AttributeError: If the specified bot is not found.

        """
        rb = getattr(import_module(f".{self.typebot.lower()}", __package__), self.typebot.lower())

        # rb = self.bots.get(self.typebot)
        if not rb:
            raise AttributeError("Robô não encontrado!!")

        return rb(**self.kwrgs)
