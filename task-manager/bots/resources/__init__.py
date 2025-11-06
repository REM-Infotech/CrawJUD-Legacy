"""Pacote público para recursos do sistema.

Contém arquivos e utilitários de recursos compartilhados.
"""

from .auth._autenticador import AutenticadorPJe
from .formatadores import formata_string
from .iterators.pje import RegioesIterator

__all__ = [
    "AutenticadorPJe",
    "RegioesIterator",
    "formata_string",
]
