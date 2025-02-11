"""Module: caixa.

This module initializes and manages the Caixa bot within the CrawJUD-Bots application.
"""

import logging
import traceback
from typing import Union

from ...common import StartError
from .emissor import Emissor

logger = logging.getLogger(__name__)
ClassBots = Union[Emissor]


class Caixa:
    """caixa class.

    Initializes and executes the Caixa bot based on provided configurations.
    """

    def __init__(
        self,
        path_args: str,
        display_name: str,
        system: str,
        typebot: str,
        logger: logging.Logger = None,
        *args: tuple[str],
        **kwargs: dict[str, str],
    ) -> None:
        """Initialize a WorkerBot instance.

        Sets up the bot and executes the bot module based on the system type.

        Args:
            path_args (str): Path to the bot's arguments file.
            display_name (str): The display name for the bot.
            system (str): The system for the bot (e.g., projudi).
            typebot (str): The type of bot (e.g., capa).
            logger (logging.Logger, optional): The logger instance.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        try:
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)
            display_name_ = args[0] if args else kwargs.pop("display_name", display_name)
            path_args_ = args[1] if args else kwargs.pop("path_args", path_args)
            system_ = args[2] if args else kwargs.pop("system", system)
            typebot_ = args[3] if args else kwargs.pop("typebot", typebot)

            self.typebot_ = typebot_

            kwargs.update({"display_name": display_name})

            caller = self.bot_call
            caller = caller(display_name=display_name_, path_args=path_args_, typebot=typebot_, system=system_)

            caller.execution()

        except Exception as e:
            err = traceback.format_exc()
            logger.exception(err)
            raise StartError(traceback.format_exc()) from e

    @property
    def bot_call(self) -> ClassBots:
        """Bot property.

        Dynamically imports and returns an instance of the specified bot type.

        Returns:
            any: An instance of the specified bot.

        Raises:
            AttributeError: If the specified bot type is not found.

        """
        bot_call = globals().get(self.typebot_.capitalize())

        # rb = self.bots.get(self.typebot)
        if not bot_call:
            raise AttributeError("Robô não encontrado!!")

        return bot_call
