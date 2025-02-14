"""Module: projudi.

This module defines the projudi class, which manages the initialization and execution
of different bot types within the CrawJUD-Bots application.
"""

from __future__ import annotations

import logging
import traceback
from typing import Callable, Union

from ...common.exceptions import StartError
from .capa import Capa
from .intimacoes import Intimacoes
from .movimentacao import Movimentacao
from .proc_parte import ProcParte as Proc_parte
from .protocolo import Protocolo

ClassBots = Union[Capa, Intimacoes, Movimentacao, Proc_parte, Protocolo]
logger = logging.getLogger(__name__)


class Projudi:
    """The projudi class initializes and executes the specified bot based on provided configurations.

    Attributes:
        kwargs (dict): Keyword arguments containing configuration parameters for the bot.

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
            display_name = kwargs.pop("display_name", args[0])
            system = kwargs.pop("system", args[2])
            typebot = kwargs.pop("typebot", args[3])
            logger = kwargs.pop("logger", logger)
            logger.info("Starting bot %s with system %s and type %s", display_name, system, typebot)

            self.typebot_ = typebot

            kwargs.update({"display_name": display_name})

            self.bot_call.initialize(*args, **kwargs).execution()

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
        bot_call: Callable[[], None] = globals().get(self.typebot_.capitalize())

        # rb = self.bots.get(self.typebot)
        if not bot_call:
            raise AttributeError("Robô não encontrado!!")

        return bot_call
