"""Initialize scripts package for CrawJUD-Bots: Projudi, Esaj, Elaw, PJe, Calc., Caixa v1.

This package provides script classes for distinct systems in the CrawJUD-Bots app.
It integrates functionality for Projudi, Esaj, Elaw, PJe, Calculadoras (Calc.), and Caixa.

Attributes:
    __all__ (list): Classes exported by this package.
    ClassesSystems (Union): Union type of all supported system classes.

"""

from typing import Union

from ..caixa import Caixa
from ..calculadoras import Calculadoras
from ..elaw import Elaw
from ..esaj import Esaj
from ..pje import PJe
from ..projudi import Projudi

__all__ = [Projudi, Esaj, Elaw, PJe, Calculadoras, Caixa]

ClassesSystems = Union[Caixa, Elaw, Esaj, Projudi, PJe, Calculadoras]
