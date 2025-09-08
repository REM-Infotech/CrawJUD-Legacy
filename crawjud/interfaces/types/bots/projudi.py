"""Tipos para robôs do PROJUDI."""

from typing import TypedDict


class DataSucessoProtocoloProjudi(TypedDict):
    """Class dict para mapear retorno de sucesso Projudi Protocolo."""

    NUMERO_PROCESSO: str
    MENSAGEM: str
    NOME_COMPROVANTE: str
    NOME_COMPROVANTE_2: str
