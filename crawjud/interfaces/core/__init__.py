"""Tipos básicos e fundamentais para o CrawJUD.

Este módulo centraliza definições de tipos primitivos, literais e customizados
que são utilizados em toda a aplicação.
"""

from __future__ import annotations

from .custom import StrProcessoCNJ, StrTime
from .literals import (
    AppName,
    CallableMethodRequest,
    MessageNadaEncontrado,
    MessageTimeoutAutenticacao,
    MethodRequested,
    MsgUsuarioAtualizado,
    MsgUsuarioCadastrado,
    MsgUsuarioDeletado,
    ReturnCallMethod,
    StatusType,
    TReturnMessageExecutBot,
    TReturnMessageMail,
    TReturnMessageUploadFile,
    TypeLog,
)
from .primitives import (
    Binds,
    DataStores,
    DictData,
    DictType,
    ListData,
    ListPartes,
    ListType,
    ProcessInfo,
    PyNumbers,
    PyStrings,
    ReturnFormataTempo,
    StrPath,
    TupleType,
)

__all__ = [
    # Custom types
    "StrProcessoCNJ",
    "StrTime",
    # Literal types
    "AppName",
    "CallableMethodRequest",
    "MessageNadaEncontrado",
    "MessageTimeoutAutenticacao",
    "MethodRequested",
    "MsgUsuarioAtualizado",
    "MsgUsuarioCadastrado",
    "MsgUsuarioDeletado",
    "ReturnCallMethod",
    "StatusType",
    "TReturnMessageExecutBot",
    "TReturnMessageMail",
    "TReturnMessageUploadFile",
    "TypeLog",
    # Primitive types
    "Binds",
    "DataStores",
    "DictData",
    "DictType",
    "ListData",
    "ListPartes",
    "ListType",
    "ProcessInfo",
    "PyNumbers",
    "PyStrings",
    "ReturnFormataTempo",
    "StrPath",
    "TupleType",
]