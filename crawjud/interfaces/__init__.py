"""Módulo de interfaces para o CrawJUD."""

from __future__ import annotations

from typing import TYPE_CHECKING

import socketio

if TYPE_CHECKING:
    import engineio


class ASyncServerType(socketio.AsyncServer):
    """Type extension for socketio.AsyncServer with an explicit AsyncServer attribute.

    Inherits from socketio.AsyncServer and adds a type annotation
    for the 'eio' attribute, which represents the underlying Engine.IO
    AsyncServer instance.
    """

    eio: engineio.AsyncServer
