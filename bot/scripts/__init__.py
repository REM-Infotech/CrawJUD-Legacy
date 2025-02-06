"""Package: scripts.

This package contains various scripts for different systems within the CrawJUD-Bots application, including projudi, esaj, elaw, pje, calculadoras, and caixa.
"""  # noqa: E501

from typing import Union  # noqa: E402

from .caixa import caixa  # noqa: E402
from .calculadoras import calculadoras  # noqa: E402
from .elaw import elaw  # noqa: E402
from .esaj import esaj  # noqa: E402
from .pje import pje  # noqa: E402
from .projudi import projudi  # noqa: E402

__all__ = [projudi, esaj, elaw, pje, calculadoras, caixa]

ClassesSystems = Union[caixa, elaw, esaj, projudi, pje, calculadoras]
