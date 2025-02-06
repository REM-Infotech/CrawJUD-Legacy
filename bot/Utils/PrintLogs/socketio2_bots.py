"""Module: socketio_bots.

This module provides a SocketBot class for handling socket.io connections and emitting events.
"""

from __future__ import annotations

from time import sleep

from socketio import Client

sio = Client()


class SocketBot:
    """A class to handle socket.io connections and emit events."""

    def __init__(self) -> None:
        """Initialize the SocketBot instance."""
        self.connected = False
        self.tries = 0

    def with_context(self, event: str, data: dict, url: str) -> None:
        """Handle the context for connecting and emitting events.

        Args:
            event (str): The event name to emit.
            data (dict): The data to send with the event.
            url (str): The URL to connect to.

        """
        try:
            url = f"https://{url}"
            # Verifica se já está conectado antes de tentar se conectar
            self.connect_emit(event, data, url)
        except Exception:
            # ...existing code...
            try:
                self.connected = False
                sio.disconnect()
                sleep(0.25)
                self.connect_emit(event, data, url)
            except Exception:
                sleep(0.25)
                # ...existing code...

    def connect_emit(self, event: str, data: dict, url: str) -> None:
        """Connect to the socket.io server and emit an event.

        Args:
            event (str): The event name to emit.
            data (dict): The data to send with the event.
            url (str): The URL to connect to.

        """
        if not self.connected:
            sio.connect(url, namespaces=["/log"])
            self.connected = True

        sio.emit(event, data, namespace="/log")

    def send_message(self, data: dict[str, str | int], url: str) -> None:
        """Send a log message to the socket.io server.

        Args:
            data (dict): The data to send with the log message.
            url (str): The URL to connect to.

        """
        self.with_context("log_message", data, url)

    def end_message(self, data: dict, url: str) -> None:
        """Send a stop bot message and a status bot message to the socket.io server.

        Args:
            data (dict): The data to send with the stop bot message.
            url (str): The URL to connect to.

        """
        try:
            pass
        finally:
            self.with_context("stop_bot", data, url)
            self.with_context("statusbot", {}, url)
