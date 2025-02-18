"""Module: esaj.

Initialize and manage the ESaj bot within the CrawJUD-Bots application.
"""

import logging
import traceback
from typing import Callable, Union

from ...common import StartError
from .busca_pags import BuscaPags as Busca_pags
from .capa import Capa
from .emissao import Emissao
from .movimentacao import Movimentacao
from .protocolo import Protocolo

logger_ = logging.getLogger(__name__)

ClassBots = Union[Emissao, Busca_pags, Capa, Movimentacao, Protocolo]


class Esaj:
    """Class Esaj.

    Initialize and execute the ESaj bot based on configuration parameters.

    Attributes:
        typebot_ (str): The type of bot to execute.

    Methods:
        __init__(args, kwargs): Initialize and run the ESaj bot.
        bot_call: Retrieve and return the bot instance based on typebot.

    """

    def __init__(self, *args: str | int, **kwargs: str | int) -> None:
        """Initialize the Esaj bot instance.

        Sets up the bot configuration and starts execution.

        Args:
            *args: Variable positional arguments.
            **kwargs: Arbitrary keyword arguments including path_args, display_name,
                      system, and typebot.

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
        """Retrieve the bot instance.

        Dynamically imports and returns an instance of the specified bot type.

        Returns:
            ClassBots: An instance of the specified bot class.

        """
        bot_call: Callable[[], None] = globals().get(self.typebot_.capitalize())

        # rb = self.bots.get(self.typebot)
        if not bot_call:
            raise AttributeError("Robô não encontrado!!")

        return bot_call
