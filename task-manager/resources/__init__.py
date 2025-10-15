"""Pacote público para recursos do sistema.

Contém arquivos e utilitários de recursos compartilhados.
"""

from unicodedata import combining, normalize

from werkzeug.utils import secure_filename


def format_string(string: str) -> str:  # noqa: D103
    normalized_string = "".join([
        c for c in normalize("NFKD", string) if not combining(c)
    ])

    return " ".join(
        secure_filename(normalized_string)
        .replace("-", "")
        .replace("_", " ")
        .split(),
    )
