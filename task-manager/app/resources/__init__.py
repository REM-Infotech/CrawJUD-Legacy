"""Pacote público para recursos do sistema.

Contém arquivos e utilitários de recursos compartilhados.
"""

from constants import MAIOR_60_ANOS, VER_RECURSO

from .auth.pje import AutenticadorPJe
from .formatadores import formata_string
from .iterators.pje import RegioesIterator

__all__ = [
    "AutenticadorPJe",
    "RegioesIterator",
    "formata_string",
]


def value_check(label: str, valor: str) -> bool:
    if label and valor and ":" not in valor:
        return valor not in {MAIOR_60_ANOS, VER_RECURSO}

    return False
