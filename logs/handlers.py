"""Handler for logs module."""

import logging
from os import getenv

import socketio
import tqdm


class SocketIOLogClientHandler(logging.Handler):
    """Logging handler that sends log messages to a Socket.IO server."""

    _app = getenv("APPLICATION_APP")
    formatter: logging.Formatter = None
    level: int = logging.INFO
    server_url: str = "http://localhost:7000"

    def __init__(self, server_url: str = "http://localhost:7000", *args: str | int, **kwargs: str | int) -> None:
        """Initialize the handler with the server URL."""
        super().__init__()
        self.sio = socketio.Client()
        self.server_url = server_url
        self._connect()
        self.formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    def _connect(self) -> None:
        try:
            self.sio.connect(
                url=self.server_url,
                namespaces=[
                    "/application_logs",
                    f"/{self._app}",
                ],
                wait_timeout=5,
            )
        except Exception as e:
            tqdm.write(f"SocketIO connection error: {e}")

    def emit(self, record: logging.LogRecord) -> None:
        """Emit the log message to the server via Socket.IO."""
        try:
            dict_record = list(record.__dict__.items())
            not_formated = {}
            for key, value in dict_record:
                try:
                    not_formated.update({
                        key: str(value),
                    })
                except Exception as e:
                    tqdm.write(f"Error: {e}")
                    continue
            msg = self.format(record)

            data = {"message": msg}
            data.update(not_formated)
            self.sio.emit(f"{self._app}_logs", data=data, namespace=f"/{self._app}")
        except Exception:
            self.handleError(record)
