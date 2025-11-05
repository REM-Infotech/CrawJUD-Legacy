from typing import TypedDict


class CapaProjudiDict(TypedDict):
    NUMERO_PROCESSO: str = ""
    COMARCA: str = ""
    COMPETENCIA: str = ""
    JUIZO: str = ""
    JUIZ: str = ""
    OBJETO_PEDIDO: str = ""
    CLASSIFICACAO_PROCESSUAL: str = ""
    SITUACAO: str = ""
    SEQUENCIAL: str = ""
    INTERVENCAO_DO_MP: str = ""
    VALOR_DA_CAUSA: str = ""
    STATUS: str = ""
    CLASSE_PROCESSUAL: str = ""
    ASSUNTO_PRINCIPAL: str = ""
    NIVEL_DE_SIGILO: str = ""


class PartesProjudiDict(TypedDict):
    NUMERO_PROCESSO: str = ""
    NOME: str = ""
    DOCUMENTO: str = ""
    CPF_CNPJ: str = ""
    ADVOGADOS: str = ""
    ENDERECO: str = ""


class RepresentantesProjudiDict(TypedDict):
    NUMERO_PROCESSO: str = ""
    NOME: str = ""
    OAB: str = ""
    REPRESENTADO: str = ""
