"""Módulo de interfaces e tipos para o CrawJUD.

Este módulo centraliza todas as definições de tipos, interfaces e estruturas
de dados utilizadas em toda a aplicação CrawJUD, organizadas por domínio:

- core: Tipos básicos, primitivos e customizados
- auth: Tipos de autenticação e sessão
- bots: Tipos relacionados aos bots
- systems: Tipos de sistemas externos (PJe, WebDriver)
- tasks: Tipos de tarefas assíncronas
- forms: Tipos de formulários
- controllers: Tipos de controladores

Também inclui a extensão ASyncServerType para socketio.AsyncServer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# Importações principais de cada domínio - apenas módulos testados e funcionais
from . import auth, core

try:
    import socketio

    _SOCKETIO_AVAILABLE = True
except ImportError:
    _SOCKETIO_AVAILABLE = False

if TYPE_CHECKING:
    import engineio


if _SOCKETIO_AVAILABLE:

    class ASyncServerType(socketio.AsyncServer):
        """Type extension for socketio.AsyncServer with an explicit AsyncServer attribute.

        Inherits from socketio.AsyncServer and adds a type annotation
        for the 'eio' attribute, which represents the underlying Engine.IO
        AsyncServer instance.
        """

        eio: engineio.AsyncServer

else:
    # Define uma classe placeholder quando socketio não está disponível
    class ASyncServerType:
        """Placeholder for ASyncServerType when socketio is not available."""


# Re-exportação dos principais tipos de cada domínio
__all__ = [
    # Módulos de domínio funcionais
    "core",
    "auth",
    # Interface específica
    "ASyncServerType",
]
