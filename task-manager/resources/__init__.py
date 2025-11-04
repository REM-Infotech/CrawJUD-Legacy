"""Pacote público para recursos do sistema.

Contém arquivos e utilitários de recursos compartilhados.
"""

from unicodedata import combining, normalize

from werkzeug.utils import secure_filename

from ._autenticador import AutenticadorPJe
from ._iterator import RegioesIterator


def format_string(string: str) -> str:  # noqa: D103
    normalized_string = "".join([
        c for c in normalize("NFKD", string) if not combining(c)
    ])

    return secure_filename(normalized_string).upper()


__all__ = ["RegioesIterator", "format_string", "AutenticadorPJe"]
