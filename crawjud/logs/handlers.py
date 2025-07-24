"""Custom logging handlers."""

import json
import logging
import logging.handlers
from os import getenv

import redis


class RedisHandler(logging.Handler):
    """Custom logging handler to send logs to Redis."""

    uri = "redis://localhost:6379"
    db = 0
    list_name = "logs"
    level: int = 10

    def __init__(
        self,
        uri: str = "redis://localhost:6379",
        db: int = 0,
        list_name: str = None,
    ) -> None:
        """Initialize the RedisHandler.

        Args:
            uri (str, optional): The Redis URI. Defaults to "redis://localhost:6379".
            db (int, optional): The Redis database. Defaults to 0.
            list_name (str, optional): The name of the list where the logs will be stored in Redis. Defaults to "logs".

        """
        super().__init__()
        self.uri = uri
        self.db = db

        if list_name is None:
            list_name = getenv("APPLICATION_APP", "logs")

        self.list_name = list_name

        self.client = redis.Redis.from_url(url=self.uri, db=self.db)  # Conexão com o Redis
        self.list_name = list_name  # Nome da lista onde os logs serão armazenados no Redis

    def emit(self, record: logging.LogRecord) -> None:
        """Emit the log record to Redis."""
        try:
            log_entry = self.format(record)  # Formata o log conforme configurado
            self.client.rpush(self.list_name, log_entry)  # Adiciona à lista no Redis
        except Exception:
            self.handleError(record)  # Captura erros ao salvar no Redis


# Criar o formato JSON para o log
class JsonFormatter(logging.Formatter):
    """Json Formatter for logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record to JSON."""
        log_data = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "module": record.module,
            "module_name": record.name,
        }
        return json.dumps(log_data)


class CustomFileHandler(logging.handlers.RotatingFileHandler):
    """Custom logging handler to send logs to a file."""

    filename = "app.logs"
    max_bytes = 1024
    backup_count = 1
    level: int = 10

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record to JSON."""
        log_data = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatter.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "module": record.module,
        }
        return json.dumps(log_data)
