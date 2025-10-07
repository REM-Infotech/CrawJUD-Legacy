"""Recursos da API."""
# Recursos da API podem ser definidos aqui futuramente.


def camel_to_snake(name: str) -> str:
    """Conversão de Strings Camel para Snake-Case.

    Returns:
        str: string convertida

    """
    import re

    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
