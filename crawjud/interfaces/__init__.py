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

import socketio

# Importações principais de cada domínio
from . import auth, bots, controllers, core, forms, systems, tasks

if TYPE_CHECKING:
    import engineio


class ASyncServerType(socketio.AsyncServer):
    """Type extension for socketio.AsyncServer with an explicit AsyncServer attribute.

    Inherits from socketio.AsyncServer and adds a type annotation
    for the 'eio' attribute, which represents the underlying Engine.IO
    AsyncServer instance.
    """

    eio: engineio.AsyncServer


# Re-exportação dos principais tipos de cada domínio
__all__ = [
    # Módulos de domínio
    "auth",
    "bots", 
    "controllers",
    "core",
    "forms",
    "systems",
    "tasks",
    # Interface específica
    "ASyncServerType",
]
