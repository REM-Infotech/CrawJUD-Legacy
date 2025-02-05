"""Provide the pje class to manage and execute the pje Bot."""

from __future__ import annotations

import logging
import traceback
from importlib import import_module
from typing import Any

from ...common import StartError


class pje:
    """Represent the pje Bot environment and handle its execution."""

    def __init__(self, **kwrgs) -> None:
        """Initialize the pje instance with the given keyword arguments."""
        self.kwrgs = kwrgs
        self.__dict__.update(kwrgs)
        try:
            self.Bot.execution()

        except Exception as e:
            logging.error(f"Exception: {e}", exc_info=True)
            raise StartError(traceback.format_exc()) from e

    @property
    def Bot(self) -> Any:
        """Return the bot instance configured for this environment."""
        rb = getattr(
            import_module(f".{self.typebot.lower()}", __package__),
            self.typebot.lower(),
        )

        # rb = self.bots.get(self.typebot)
        if not rb:
            raise AttributeError("Robô não encontrado!!")

        return rb(**self.kwrgs)
