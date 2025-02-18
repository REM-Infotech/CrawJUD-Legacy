"""Module: caixa.

Initializes and manages the Caixa bot within the CrawJUD-Bots application.
It provides a class interface to run the Emissor bot and handle errors.
"""

import logging
import traceback
from typing import Callable, Union

from ...common import StartError
from .emissor import Emissor

logger_ = logging.getLogger(__name__)
ClassBots = Union[Emissor]


class Caixa:
    """Class Caixa.

    Initializes and executes the specified bot (Emissor) based on
    provided configurations.
    """

    def __init__(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Initialize the Caixa bot.

        Sets up the bot and then executes the bot's main module
        based on the specified system type.

        Args:
            *args: Additional positional arguments for the bot.
            **kwargs: Additional keyword arguments. Might include:
                path_args (str): Path to the bot's arguments file.
                display_name (str): Bot's visible name.
                system (str): The system for the bot (e.g., 'projudi').
                typebot (str): Type of bot to instantiate (e.g., 'capa').
                logger (logging.Logger): The logger instance (optional).

        Raises:
            StartError: If there is any exception during initialization.

        """
        try:
            display_name = kwargs.get("display_name")
            system = kwargs.get("system")
            typebot = kwargs.get("typebot")
            logger = kwargs.get("logger", logger_)
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)

            self.typebot_ = typebot

            self.bot_call.initialize(*args, **kwargs).execution()

        except Exception as e:
            err = traceback.format_exc()
            logger.exception(err)
            raise StartError(traceback.format_exc()) from e

    @property
    def bot_call(self) -> ClassBots:
        """Return a dynamic reference to the bot class.

        Uses the typebot_ attribute to retrieve the corresponding
        bot class (e.g., Emissor) and return an instance to handle
        the process logic.

        Returns:
            ClassBots: An instance of the requested bot class.

        Raises:
            AttributeError: If the specified bot type is not found.

        """
        bot_call: Callable[[], None] = globals().get(self.typebot_.capitalize())

        # rb = self.bots.get(self.typebot)
        if not bot_call:
            raise AttributeError("Robô não encontrado!!")

        return bot_call
