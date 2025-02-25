import logging
import redis
import json


class RedisHandler(logging.Handler):
    """Custom logging handler to send logs to Redis."""

    uri = "redis://localhost:6379"
    db = 0
    list_name = "logs"

    def __init__(
        self,
        uri: str = "redis://localhost:6379",
        db: int = 0,
        list_name: str = "logs",
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
        }
        return json.dumps(log_data)
