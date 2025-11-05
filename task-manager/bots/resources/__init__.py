"""Pacote público para recursos do sistema.

Contém arquivos e utilitários de recursos compartilhados.
"""

from ._formatadores import formata_string
from .auth._autenticador import AutenticadorPJe
from .iterators.pje import RegioesIterator

__all__ = [
    "RegioesIterator",
    "AutenticadorPJe",
    "formata_string",
]
