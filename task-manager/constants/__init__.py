"""Constantes do gerenciador de tarefas."""

from pathlib import Path
from re import Pattern

WORKDIR = Path(__file__).cwd()

HTTP_STATUS_FORBIDDEN = 403
COUNT_TRYS = 15

PADRAO_CNJ: list[Pattern] = [r"^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$"]
CSS_INPUT_PROCESSO = {
    "1": "#numeroProcesso",
    "2": "#numeroRecurso",
}

PADRAO_DATA: list[Pattern] = [
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$",
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}$",
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}Z$",
    r"^\d{4}-\d{2}-\d{2}"
    r"^\d{2}:\d{2}:\d{2}$",
    r"^\d{4}-\d{2}-\d{2}.\d{1,6}$",
]
