"""
Module for configuration properties of web elements.

Defines the Configuracao class that manages properties for each expected element.
"""


class Configuracao:
    """Define propriedades específicas para cada elemento esperado."""

    def __init__(self, dados):
        """
        Initialize the Configuracao with element data.

        Args:
            dados: The data containing element properties.
        """
        self.element_data = dados

    def __getattr__(self, name: str) -> str:
        """
        Retrieve the property of a given element by name.

        Args:
            name (str): The name of the element property.

        Returns:
            str: The property value of the element.

        Raises:
            AttributeError: If the element with the given name is not found.
        """
        element = self.element_data.get(name)
        if not element:
            raise AttributeError(f"Elemento {name} não encontrado")

        return element
