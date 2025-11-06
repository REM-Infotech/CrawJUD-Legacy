"""Dicionários para salvamento em planilha."""

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from datetime import datetime


class CapaPJe(TypedDict):
    """Defina o dicionário para salvar dados da planilha de processos PJE.

    Args:
        ID_PJE (int): Identificador único do processo no PJE.
        LINK_CONSULTA (str): URL para consulta do processo.
        NUMERO_PROCESSO (str): Número do processo judicial.
        CLASSE (str): Classe judicial do processo.
        SIGLA_CLASSE (str): Sigla da classe judicial.
        DATA_DISTRIBUICAO (datetime): Data de distribuição do processo.
        STATUS_PROCESSO (str): Status atual do processo.
        SEGREDO_JUSTICA (str): Indica se o processo está em segredo de justiça.

    Returns:
        CapaPJe: Dicionário tipado com os dados do processo.

    """

    ID_PJE: int
    LINK_CONSULTA: str
    NUMERO_PROCESSO: str
    CLASSE: str
    SIGLA_CLASSE: str
    ORGAO_JULGADOR: str
    SIGLA_ORGAO_JULGADOR: str
    DATA_DISTRIBUICAO: datetime
    STATUS_PROCESSO: str
    SEGREDO_JUSTICA: str


class AudienciasProcessos(TypedDict):
    """Defina os campos das audiências do processo judicial no padrão PJe.

    Args:
        ID_PJE (int): Identificador único do processo no PJE.
        NUMERO_PROCESSO (str): Número do processo judicial.
        TIPO_AUDIENCIA (str): Tipo da audiência.
        MODO_AUDIENCIA (str): Modo de realização da audiência.
        STATUS (str): Status da audiência.

    Returns:
        AudienciasProcessos: Dicionário tipado com os dados da audiência.

    """

    ID_PJE: int
    NUMERO_PROCESSO: str
    TIPO_AUDIENCIA: str
    MODO_AUDIENCIA: str
    STATUS: str
    DATA_INICIO: str
    DATA_FIM: str
    DATA_MARCACAO: str


class Partes(TypedDict):
    """Defina os campos das partes do processo judicial no padrão PJe.

    Args:
        ID_PJE (int): Identificador único do processo no PJE.
        NOME (str): Nome da parte.
        CPF (str): CPF da parte.
        TIPO_PESSOA (str): Tipo da pessoa (física/jurídica).
        PROCESSO (str): Número do processo.
        POLO (str): Polo da parte (ativo/passivo).
        PARTE_PRINCIPAL (bool): Indica se é parte principal.
        TIPO_PARTE (str): Tipo da parte no processo.

    Returns:
        Partes: Dicionário tipado com os dados da parte.

    """

    ID_PJE: int
    NOME: str
    DOCUMENTO: str
    TIPO_DOCUMENTO: str
    TIPO_PARTE: str
    TIPO_PESSOA: str
    PROCESSO: str
    POLO: str
    PARTE_PRINCIPAL: bool


class Representantes(TypedDict):
    """Defina os campos dos representantes das partes do processo judicial no padrão PJe.

    Args:
        ID_PJE (int): Identificador único do processo no PJE.
        NOME (str): Nome do representante.
        CPF (str): CPF do representante.
        PARTE_PRINCIPAL (bool): Indica se é parte principal.
        TIPO_PARTE (str): Tipo da parte representada.
        TIPO_PESSOA (str): Tipo da pessoa (física/jurídica).
        PROCESSO (str): Número do processo.
        POLO (str): Polo da parte (ativo/passivo).
        OAB (str): Número de inscrição na OAB.
        EMAILS (str): E-mails do representante.
        TELEFONE (str): Telefone do representante.

    Returns:
        Representantes: Dicionário tipado com os dados do representante.

    """

    ID_PJE: int
    NOME: str
    DOCUMENTO: str
    TIPO_DOCUMENTO: str
    REPRESENTADO: str
    TIPO_PARTE: str
    TIPO_PESSOA: str
    PROCESSO: str
    POLO: str
    OAB: str
    EMAILS: str
    TELEFONE: str


class Assuntos(TypedDict):
    """Defina os campos dos assuntos do processo judicial no padrão PJe.

    Args:
        ID_PJE (int): Identificador único do processo no PJE.
        PROCESSO (str): Número do processo judicial.
        ASSUNTO_COMPLETO (str): Descrição completa do assunto.
        ASSUNTO_RESUMIDO (str): Descrição resumida do assunto.

    Returns:
        Assuntos: Dicionário tipado com os dados dos assuntos.

    """

    ID_PJE: int
    PROCESSO: str
    ASSUNTO_COMPLETO: str
    ASSUNTO_RESUMIDO: str
