from typing import Literal, TypedDict

from __types import MessageType, PolosProcessuais, StatusBot


class Message(TypedDict, total=False):
    pid: str
    message: str
    message_type: MessageType
    status: StatusBot
    start_time: str
    row: int
    total: int
    error_count: int
    success_count: int
    remaining_count: int


class ColorsDict(TypedDict):
    info: Literal["cyan"]
    log: Literal["yellow"]
    error: Literal["red"]
    warning: Literal["magenta"]
    success: Literal["green"]


class DataSucesso(TypedDict):
    NUMERO_PROCESSO: str
    MENSAGEM: str
    NOME_COMPROVANTE: str
    NOME_COMPROVANTE_2: str


class BotData(TypedDict):
    """TypedDict for bot data."""

    NUMERO_PROCESSO: str
    GRAU: int | str
    POLO_PARTE: PolosProcessuais
    FORO: str  # ESAJ EMISSAO | ELAW CADASTRO
    VALOR_CALCULADO: str  # CAIXA | CALCULADORA TJDFT
    ADVOGADO_INTERNO: str  # ELAW CADASTRO | ELAW COMPLEMENTO
    TIPO_EMPRESA: str  # ELAW CADASTRO | ELAW COMPLEMENTO
    VARA: str  # CAIXIA | ELAW CADASTRO | ELAW COMPLEMENTO
    COMARCA: str  # CAIXIA | ELAW CADASTRO | ELAW COMPLEMENTO

    TIPO_GUIA: str  # ELAW SOLICITACAO DE PAGAMENTO | ESAJ EMISSAO
    VALOR_CAUSA: str  # ELAW CADASTRO | ELAW COMPLEMENTO | ESAJ EMISSAO

    # CAIXA EMISSÃO GUIAS
    TRIBUNAL: str
    AGENCIA: str
    TIPO_ACAO: str
    AUTOR: str
    CPF_CNPJ_AUTOR: str
    REU: str
    CPF_CNPJ_REU: str
    NOME_CUSTOM: str
    TEXTO_DESC: str
    DATA_PGTO: str
    VIA_CONDENACAO: str

    # CALCULADORA TJDFT
    REQUERENTE: str
    REQUERIDO: str
    JUROS_PARTIR: str
    JUROS_PERCENT: str
    DATA_INCIDENCIA: str
    DATA_CALCULO: str
    MULTA_PERCENTUAL: str
    MULTA_DATA: str
    HONORARIO_SUCUMB_PERCENT: str
    HONORARIO_SUCUMB_DATA: str
    HONORARIO_SUCUMB_VALOR: str
    HONORARIO_SUCUMB_PARTIR: str
    PERCENT_MULTA_475J: str
    HONORARIO_CUMPRIMENTO_PERCENT: str
    HONORARIO_CUMPRIMENTO_DATA: str
    HONORARIO_CUMPRIMENTO_VALOR: str
    HONORARIO_CUMPRIMENTO_PARTIR: str
    CUSTAS_DATA: str
    CUSTAS_VALOR: str

    # ELAW ANDAMENTOS
    ANEXOS: list[str]
    DATA: str
    OCORRENCIA: str
    OBSERVACAO: str

    # ELAW CADASTRO
    AREA_DIREITO: str
    SUBAREA_DIREITO: str
    ESTADO: str
    EMPRESA: str
    PARTE_CONTRARIA: str
    ADV_PARTE_CONTRARIA: str
    TIPO_PARTE_CONTRARIA: str
    DOC_PARTE_CONTRARIA: str
    CAPITAL_INTERIOR: str
    ACAO: str
    DATA_DISTRIBUICAO: str
    ESCRITORIO_EXTERNO: str

    # ELAW COMPLEMENTO
    ESFERA: str
    UNIDADE_CONSUMIDORA: str
    LOCALIDADE: str
    BAIRRO: str
    DIVISAO: str
    DATA_CITACAO: str
    FASE: str
    PROVIMENTO: str
    FATO_GERADOR: str
    DESC_OBJETO: str
    OBJETO: str

    # ELAW DOWNLOAD DOCUMENTOS
    TERMOS: str

    # ELAW PROVISIONAMENTO
    PROVISAO: str
    DATA_BASE_CORRECAO: str
    DATA_BASE_JUROS: str
    VALOR_ATUALIZACAO: str
    OBSERVACAO: str

    # ELAW SOLICITACAO DE PAGAMENTO
    TIPO_PAGAMENTO: str
    VALOR_GUIA: str
    DOC_GUIA: str
    DOC_CALCULO: str
    TIPO_CONDENACAO: str
    DESC_PAGAMENTO: str
    DATA_LANCAMENTO: str
    CNPJ_FAVORECIDO: str
    COD_BARRAS: str
    SOLICITANTE: str

    # ESAJ EMISSAO
    CLASSE: str
    NOME_INTERESSADO: str
    CPF_CNPJ: str
    PORTAL: str

    # ESAJ | PROJUDI | PJE CAPA
    TRAZER_COPIA: str

    #  ESAJ | PROJUDI | PJE MOVIMENTACAO | JUSDS PRAZO
    PALAVRAS_CHAVE: str
    DATA_INICIO: str
    DATA_FIM: str
    INTIMADO: str
    DOC_SEPARADOR: str
    TRAZER_TEOR: str
    USE_GPT: str
    TRAZER_PDF: str

    #  ESAJ | PROJUDI | PJE PROTOCOLO
    ANEXOS: str
    TIPO_PROTOCOLO: str
    TIPO_ARQUIVO: str
    TIPO_ANEXOS: str
    SUBTIPO_PROTOCOLO: str
    PETICAO_PRINCIPAL: str
    PARTE_PETICIONANTE: str

    TIPO: str
    SUBTIPO: str
    DESCRICAO: str
    ATRIBUIR_PARA: str
    SITUACAO_EXECUCAO: str
    VALOR_MULTA: str
    VALOR_PGTO: str
    DATA_ATUALIZACAO: str
    NUMERO_COMPROMISSO: str

    NUMERO_CHAMADO: str
