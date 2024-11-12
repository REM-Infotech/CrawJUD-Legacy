# Criar loggers personalizados
import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

info_logger = None
warning_logger = None
error_logger = None


def loggerConfig() -> None:

    path_logs = Path(os.path.join(os.getcwd(), "app", "logs"))
    path_logs.mkdir(exist_ok=True)

    # Configuração do logger principal para a aplicação Flask
    app_logger = logging.getLogger("flask_app")
    app_logger.setLevel(logging.DEBUG)  # Nível mínimo de log
    # Handler de arquivo com rotação
    file_handler = RotatingFileHandler(
        os.path.join(path_logs, "flask_app.log"), maxBytes=1000000, backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    app_logger.addHandler(file_handler)

    # Desabilitar log no terminal
    for handler in app_logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            app_logger.removeHandler(handler)

    # Configuração do logger para o Flask-SocketIO
    socketio_logger = logging.getLogger("socketio")
    socketio_logger.setLevel(logging.DEBUG)
    # Handler para o Flask-SocketIO (salvando em um arquivo separado)
    socketio_file_handler = RotatingFileHandler(
        os.path.join(path_logs, "socketio.log"), maxBytes=1000000, backupCount=3
    )
    socketio_file_handler.setLevel(logging.DEBUG)
    socketio_file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    socketio_logger.addHandler(socketio_file_handler)

    global info_logger
    info_logger = logging.getLogger("info_logger")

    global warning_logger
    warning_logger = logging.getLogger("warning_logger")

    global error_logger
    error_logger = logging.getLogger("error_logger")
