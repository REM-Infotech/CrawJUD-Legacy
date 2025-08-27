"""Agrupamento de Literais."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

type MessageNadaEncontrado = Literal["Nenhum processo encontrado"]
type MessageTimeoutAutenticacao = Literal[
    "Tempo de espera excedido para validação de sessão"
]

type AppName = Literal["Quart", "Worker"]
type TypeLog = Literal["log", "success", "warning", "info", "error"]
type StatusType = Literal[
    "Inicializando",
    "Em Execução",
    "Finalizado",
    "Falha",
]
type TReturnMessageMail = Literal["E-mail enviado com sucesso!"]
type TReturnMessageExecutBot = Literal["Execução encerrada com sucesso!"]
type TReturnMessageUploadFile = Literal["Arquivo enviado com sucesso!"]
type MethodRequested = Literal["INSERT", "UPDATE", "DELETE"]

# Mensagem de operações na tabela de usuários
type MsgUsuarioCadastrado = Literal["Usuário Cadastrado com sucesso!"]
type MsgUsuarioDeletado = Literal["Usuário deletado com sucesso!"]
type MsgUsuarioAtualizado = Literal["Informações atualizadas com sucesso!"]
type ReturnCallMethod = (
    MsgUsuarioCadastrado | MsgUsuarioAtualizado | MsgUsuarioDeletado
)

type CallableMethodRequest = Callable[[dict[str, str]], ReturnCallMethod]
