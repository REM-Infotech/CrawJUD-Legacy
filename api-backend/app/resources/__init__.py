"""Recursos da API."""

import re
from unicodedata import combining, normalize

from werkzeug.utils import secure_filename


def camel_to_snake(name: str) -> str:
    """Convenção de uma string CamelCase para snake_case.

    Returns:
        str: String convertida para snake_case.

    """
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


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
