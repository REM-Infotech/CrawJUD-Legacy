"""Recursos da API."""

import re


def camel_to_snake(name: str) -> str:
    """Convenção de uma string CamelCase para snake_case.

    Returns:
        str: String convertida para snake_case.

    """
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
