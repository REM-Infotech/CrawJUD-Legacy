"""Pacote público para recursos do sistema.

Contém arquivos e utilitários de recursos compartilhados.
"""

from __future__ import annotations

from unicodedata import combining, normalize

from werkzeug.utils import secure_filename

from . import _varas_dict

__all__ = ["_varas_dict"]


def format_string(string: str) -> str:
    normalized_string = "".join([
        c for c in normalize("NFKD", string) if not combining(c)
    ])

    return secure_filename(normalized_string)
