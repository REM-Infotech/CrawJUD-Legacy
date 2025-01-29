class Configuracao:
    """Define propriedades específicas para cada elemento esperado."""

    def __init__(self, dados):
        self.element_data = dados

    def __getattr__(self, name: str) -> str:
        element = self.element_data.get(name)
        if not element:
            raise AttributeError(f"Elemento {name} não encontrado")

        return element
