"""Pacote público para recursos do sistema.

Contém arquivos e utilitários de recursos compartilhados.
"""

from __future__ import annotations

from pathlib import Path
from unicodedata import combining, normalize

from werkzeug.utils import secure_filename

from . import _varas_dict

workdir = Path(__file__).cwd()

__all__ = ["_varas_dict", "workdir"]


def check_cors_allowed_origins(*args: T, **kwargs: T) -> bool:
    return True


def format_string(string: str) -> str:
    normalized_string = "".join([
        c for c in normalize("NFKD", string) if not combining(c)
    ])

    return " ".join(
        secure_filename(normalized_string)
        .replace("-", "")
        .replace("_", " ")
        .split(),
    )
