"""Defina estruturas tipadas para formulários administrativos do FormBot.

Este módulo fornece os dicionários tipados utilizados para autenticação e envio
de múltiplos arquivos em formulários administrativos, garantindo clareza e
segurança na manipulação dos dados recebidos.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from werkzeug.datastructures import FileMultiDict


class AdministrativoFormFileAuth(TypedDict):
    """Defina o dicionário tipado para autenticação de arquivos no administrativo.

    Args:
        xlsx (FileMultiDict): Arquivo principal do tipo xlsx.
        creds (str): Credenciais do usuário.
        client (str): Nome do cliente.
        confirm_fields (bool): Indica se os campos foram confirmados.
        periodic_task (bool): Indica se a tarefa é periódica.
        task_name (str | None): Nome da tarefa, se aplicável.
        task_hour_minute (str | None): Horário da tarefa, se aplicável.
        email_notify (str | None): E-mail para notificação, se aplicável.
        days_task (list | None): Dias para execução da tarefa, se aplicável.

    Returns:
        TypedDict: Estrutura contendo os dados de autenticação do formulário.

    """

    xlsx: FileMultiDict
    creds: str
    client: str
    confirm_fields: bool
    periodic_task: bool
    task_name: str | None
    task_hour_minute: str | None
    email_notify: str | None
    days_task: list | None


class AdministrativoFormMultipleFiles(TypedDict):
    """Defina o dicionário tipado para múltiplos arquivos no formulário administrativo.

    Args:
        xlsx (FileMultiDict): Arquivo principal do tipo xlsx.
        otherfiles (list[FileMultiDict]): Lista de outros arquivos enviados.
        creds (str): Credenciais do usuário.
        state (str): Estado do processo.
        confirm_fields (bool): Indica se os campos foram confirmados.
        periodic_task (bool): Indica se a tarefa é periódica.
        task_name (str | None): Nome da tarefa, se aplicável.
        task_hour_minute (str | None): Horário da tarefa, se aplicável.
        email_notify (str | None): E-mail para notificação, se aplicável.
        days_task (list | None): Dias para execução da tarefa, se aplicável.

    Returns:
        TypedDict: Estrutura contendo os dados do formulário administrativo.

    """

    xlsx: FileMultiDict
    otherfiles: list[FileMultiDict]
    creds: str
    state: str
    confirm_fields: bool
    periodic_task: bool
    task_name: str | None
    task_hour_minute: str | None
    email_notify: str | None
    days_task: list | None
