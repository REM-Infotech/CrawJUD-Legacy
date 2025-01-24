from importlib import import_module
from typing import Union

from ...shared import PropertiesCrawJUD
from .elaw import ELAW_AME
from .esaj import ESAJ_AM
from .pje import PJE_AM
from .projudi import PROJUDI_AM


class BaseElementsBot(PropertiesCrawJUD):

    # system = ""
    # state_or_client = ""

    def __init__(self, *args, **kwrgs) -> None:
        """### ElementsBot"""

        state_or_client = self.state_or_client

        if " - " in state_or_client:
            state_or_client = state_or_client.split(" - ")[0]

        self.objeto: Union[ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM] = getattr(
            import_module(f".{self.system.lower()}", __package__),
            f"{self.system.upper()}_{state_or_client.upper()}",
        )

    @property
    def Elements(self) -> Union[ELAW_AME, ESAJ_AM, PJE_AM, PROJUDI_AM]:
        """Retorna a configuração de acordo com o estado ou cliente."""

        return self.objeto


class ElementsBot(BaseElementsBot):

    def __init__(self, *args, **kwrgs) -> None:
        BaseElementsBot.__init__(self, *args, **kwrgs)
