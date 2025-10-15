"""Types dos bots CrawJUD."""

from typing import TypedDict


class DataSucesso(TypedDict):
    """Class dict para mapear retorno de sucesso."""

    NUMERO_PROCESSO: str
    MENSAGEM: str
    NOME_COMPROVANTE: str
    NOME_COMPROVANTE_2: str
