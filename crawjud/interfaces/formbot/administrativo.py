# noqa: D100
from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from werkzeug.datastructures import FileMultiDict


class AdministrativoFormFileAuth(TypedDict):  # noqa: D101
    xlsx: FileMultiDict
    creds: str
    client: str
    confirm_fields: bool
    periodic_task: bool
    task_name: str | None
    task_hour_minute: str | None
    email_notify: str | None
    days_task: list | None


class AdministrativoFormMultipleFiles(TypedDict):  # noqa: D101
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
