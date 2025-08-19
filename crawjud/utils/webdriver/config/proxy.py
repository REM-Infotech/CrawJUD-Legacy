"""Configura e define estruturas para manipulação de proxy e geração de HAR.

Este módulo provê:
- Função para configurar proxy com BrowserMob Proxy;
- Estruturas de dados para HAR, requests, responses, cookies e headers;
- Tipos fortemente tipados para facilitar integração e análise de tráfego HTTP.

"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict

from browsermobproxy import Client, Server
from dotenv import dotenv_values

environ = dotenv_values()


def configure_proxy() -> tuple[Client, Server]:
    """Configure e inicialize o proxy BrowserMob Proxy para captura de tráfego HTTP.

    Returns:
        tuple[Client, Server]: Retorna uma tupla contendo o cliente e o servidor do
        BrowserMob Proxy configurados e prontos para uso.


    """
    # Inicializa o servidor do BrowserMob Proxy
    server = Server()
    server.start()
    # Cria e retorna o proxy junto com o servidor
    return server.create_proxy(), server


@dataclass(frozen=True)
class CreatorInfo:
    """Defina e armazene informações do criador do arquivo HAR exportado.

    Forneça nome, versão e comentário do criador para inclusão em arquivos HAR.

    Args:
        name (str): Nome do criador do HAR.
        version (str): Versão do criador.
        comment (str): Comentário adicional.

    Returns:
        CreatorInfo: Instância imutável com informações do criador do HAR.

    """

    # Nome do criador do HAR
    name: str = "BrowserMob Proxy"
    # Versão do criador
    version: str = "2.1.4"
    # Comentário adicional
    comment: str = ""


@dataclass(frozen=True)
class HARProxy:
    """Armazene informações completas de um arquivo HAR exportado para análise.

    Estrutura o arquivo HAR com criador, versão, páginas, entradas e comentários.

    Args:
        creator (CreatorInfo): Informações do criador do HAR.
        version (str): Versão do formato HAR.
        pages (list[Page]): Lista de páginas capturadas.
        entries (list[EntryRequest]): Lista de entradas de requisições.
        comment (str): Comentário adicional.

    Returns:
        HARProxy: Instância imutável representando um arquivo HAR completo.

    """

    creator: CreatorInfo
    version: str = ""
    pages: list[Page] = field(default_factory=list)
    entries: list[EntryRequest] = field(default_factory=list)
    comment: str = ""


@dataclass(frozen=True)
class EntryRequest:
    """Armazene uma entrada de requisição HTTP para inclusão em arquivos HAR.

    Representa uma requisição HTTP capturada, incluindo dados de request, response,
    cache, timings, IP do servidor, comentários e tempo total.

    Args:
        pageref (str): Referência à página associada à requisição.
        startedDateTime (str): Data e hora de início da requisição.
        request (RequestData): Dados detalhados da requisição HTTP.
        response (ResponseData): Dados detalhados da resposta HTTP.
        cache (dict[str, str]): Informações de cache relacionadas à requisição.
        timings (dict[str, str | int]): Tempos de execução da requisição.
        serverIPAddress (str): Endereço IP do servidor de destino.
        comment (str): Comentário adicional.
        time (int): Tempo total da requisição em milissegundos.

    Returns:
        EntryRequest: Instância imutável representando uma entrada de requisição HAR.

    """

    pageref: str = "default"
    startedDateTime: str = "2025-07-29T12:15:00.626-04:00"
    request: RequestData = field(default_factory=dict)
    response: ResponseData = field(default_factory=dict)
    cache: dict[str, str] = field(default_factory=dict)
    timings: dict[str, str | int] = field(default_factory=dict)
    serverIPAddress: str = ""
    comment: str = ""
    time: int = 0


@dataclass(frozen=True)
class RequestData:
    """Armazene dados detalhados de uma requisição HTTP para arquivos HAR.

    Estrutura informações de método, versão, URL, tamanhos, cookies, headers e query.

    Args:
        method (str): Método HTTP utilizado na requisição.
        httpVersion (str): Versão do protocolo HTTP.
        url (str): URL de destino da requisição.
        headersSize (int): Tamanho dos headers enviados.
        bodySize (int): Tamanho do corpo da requisição.
        comment (str): Comentário adicional.
        cookies (list[Cookie]): Lista de cookies enviados.
        headers (list[Header]): Lista de headers enviados.
        queryString (list[str]): Lista de parâmetros de query string.

    Returns:
        RequestData: Instância imutável representando dados de uma requisição HTTP.

    """

    method: str
    httpVersion: str
    url: str
    headersSize: int
    bodySize: int
    comment: str
    cookies: list[Cookie] = field(default_factory=list)
    headers: list[Header] = field(default_factory=list)
    queryString: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResponseData:
    """Armazene dados detalhados de uma resposta HTTP para arquivos HAR exportados.

    Estrutura status, texto, versão, conteúdo, redirecionamento, tamanhos, cookies e headers.

    Args:
        status (int): Código de status HTTP.
        statusText (str): Texto do status HTTP.
        httpVersion (str): Versão do protocolo HTTP.
        content (ContentData): Conteúdo da resposta.
        redirectURL (str): URL de redirecionamento.
        headersSize (int): Tamanho dos headers.
        bodySize (int): Tamanho do corpo.
        comment (str): Comentário adicional.
        cookies (list[Cookie]): Lista de cookies recebidos.
        headers (list[Header]): Lista de headers recebidos.

    Returns:
        ResponseData: Instância imutável representando dados de uma resposta HTTP.

    """

    status: int
    statusText: str
    httpVersion: str
    content: ContentData
    redirectURL: str
    headersSize: int
    bodySize: int
    comment: str
    cookies: list[Cookie] = field(default_factory=list)
    headers: list[Header] = field(default_factory=list)


class ContentData(TypedDict):
    """Armazene dados de conteúdo de resposta HTTP para arquivos HAR exportados.

    Estrutura tamanho, tipo MIME, comentário e texto do conteúdo da resposta.

    Args:
        size (int): Tamanho do conteúdo.
        mimeType (str): Tipo MIME do conteúdo.
        comment (str): Comentário adicional.
        text (str): Texto do conteúdo (opcional).

    """

    size: int
    mimeType: str
    comment: str
    text: str = ""


class Header(TypedDict):
    """Armazene informações de header HTTP para inclusão em arquivos HAR exportados.

    Estrutura nome e valor do header.

    Args:
        name (str): Nome do header.
        value (str): Valor do header.

    """

    name: str = ""
    value: str = ""


class Cookie(TypedDict):
    """Armazene informações de cookie HTTP para inclusão em arquivos HAR exportados.

    Estrutura nome, valor, path, domínio, flags e atributos do cookie.

    Args:
        name (str): Nome do cookie.
        value (str): Valor do cookie.
        path (str): Caminho do cookie.
        domain (str): Domínio do cookie.
        secure (bool): Indica se é seguro.
        httpOnly (bool): Indica se é httpOnly.
        expiry (int): Expiração do cookie.
        sameSite (str): Política SameSite.

    """

    name: str = ""
    value: str = ""
    path: str = ""
    domain: str = ""
    secure: bool = False
    httpOnly: bool = False
    expiry: int = 0
    sameSite: str = ""


class Page(TypedDict):
    """Armazene informações de página para inclusão em arquivos HAR exportados.

    Estrutura id, data/hora de início, título, tempos e comentário da página.

    Args:
        id (str): Identificador da página.
        startedDateTime (str): Data/hora de início da página.
        title (str): Título da página.
        pageTimings (dict[str, str | int]): Tempos da página.
        comment (str): Comentário adicional.

    """

    id: str = "default"
    startedDateTime: str = "2025-07-29T12:15:00.124-04:00"
    title: str = "default"
    pageTimings: dict[str, str | int]
    comment: str = ""


class DictHARProxy(TypedDict):
    """Armazene estrutura dicionário para um arquivo HAR exportado.

    Estrutura versão, criador, páginas, entradas e comentário do HAR.

    Args:
        version (str): Versão do HAR.
        creator (CreatorInfo): Informações do criador.
        pages (list[Page]): Lista de páginas.
        entries (list[EntryRequest]): Lista de entradas.
        comment (str): Comentário adicional.

    """

    version: str = ""
    creator: CreatorInfo
    pages: list[Page]
    entries: list[EntryRequest]
    comment: str = ""
