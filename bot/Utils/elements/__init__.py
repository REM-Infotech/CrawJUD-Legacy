"""Module for the ElementsBot class, which configures and retrieves an elements bot instance based on the system and state_or_client attributes.

Classes:
    ElementsBot: A class that configures and retrieves an elements bot instance.

Methods:
    __init__: Initializes the ElementsBot instance.
    Config: Configures the elements_bot attribute by dynamically importing a module based on the system and state_or_client attributes.
    Elements: Retrieves the elements bot instance.

Attributes:
    elements_bot: Stores the elements bot instance.

"""

from __future__ import annotations

from importlib import import_module
from typing import Self, Union

from ...core import CrawJUD
from .elaw import ELAW_AME
from .esaj import ESAJ_AM
from .pje import PJE_AM
from .projudi import PROJUDI_AM


class ElementsBot(CrawJUD):
    """ElementsBot class for configuring and retrieving elements bot instances.

    This class inherits from CrawJUD and provides methods to configure the elements_bot attribute
    and retrieve the configured elements bot instance.

    Attributes:
        elements_bot (Optional[Union[ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM]]): The elements bot instance.

    Methods:
        __init__(): Initializes the ElementsBot instance.
        Config() -> Self: Configures the elements_bot attribute.
        Elements() -> Union[ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM]: Retrieves the elements bot instance.

    """

    elements_bot = None

    def __init__(self) -> None:
        """Initialize the ElementsBot instance.

        This method initializes the ElementsBot instance by calling the __init__ method of the CrawJUD class.
        """
        super().__init__()

    def config(self) -> Self:
        """Configure the elements_bot attribute.

        This method checks if the elements_bot attribute is None. If it is, it dynamically imports a module based on the
        system and state_or_client attributes of the instance, and assigns the corresponding class to the elements_bot attribute.

        Returns:
            Self: The instance with the configured elements_bot attribute.

        """
        if self.elements_bot is None:
            self.elements_bot = getattr(import_module(f".{self.system.lower()}", __package__), f"{self.system.upper()}_{self.state_or_client.upper()}")

        return self

    @property
    def Elements(self) -> Union[ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM]:  # noqa: N802
        """Retrieve the elements bot instance.

        Returns:
            Union[ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM]: The elements bot instance.

        """
        return self.elements_bot

    # @property
    # def Elements(self) -> Union[ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM]:
    #     """Retorna a configuração de acordo com o estado ou cliente."""

    #     return self.objeto
