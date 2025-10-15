"""Defina tipos de dicionário para sessão autenticada e usuários na aplicação.

Este módulo fornece:
- CurrentUser: tipo para dados do usuário autenticado;
- LicenseUserDict: tipo para dados de licença do usuário;
- SessionDict: tipo para dados completos da sessão autenticada.

"""

from __future__ import annotations

from typing import TypedDict


class CurrentUser(TypedDict):
    """Defina os campos obrigatórios para o usuário atual autenticado na sessão.

    Args:
        id (int): Identificador único do usuário.
        login (str): Nome de login do usuário.
        nome_usuario (str): Nome completo do usuário.
        email (str): Endereço de e-mail do usuário.

    Returns:
        dict: Dicionário contendo os dados do usuário autenticado.

    """

    id: int
    login: str
    nome_usuario: str
    email: str


class LicenseUserDict(TypedDict):
    """Defina os campos obrigatórios para o objeto de licença do usuário na sessão.

    Args:
        id (int): Identificador único do usuário da licença.
        name_client (str): Nome do cliente associado à licença.
        cpf_cnpj (str): CPF ou CNPJ do cliente.
        license_token (str): Token da licença do usuário.

    Returns:
        dict: Dicionário contendo os dados da licença do usuário.

    """

    id: int
    name_client: str
    cpf_cnpj: str
    license_token: str


class SessionDict(TypedDict):
    """Defina os campos obrigatórios para o dicionário de sessão autenticada.

    Args:
        accessed (bool): Indica se a sessão foi acessada.
        modified (bool): Indica se a sessão foi modificada.
        new (bool): Indica se a sessão é nova.
        permanent (bool): Indica se a sessão é permanente.
        sid (str): Identificador único da sessão.
        _permanent (bool): Flag interna de permanência da sessão.
        current_user (CurrentUser): Dados do usuário autenticado.
        license_object (LicenseUserDict): Dados da licença do usuário.

    Returns:
        dict: Dicionário contendo os dados da sessão autenticada.

    """

    accessed: bool
    modified: bool
    new: bool
    permanent: bool
    sid: str
    _permanent: bool
    current_user: CurrentUser
    license_object: LicenseUserDict
