"""Constantes do gerenciador de tarefas."""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from re import Pattern

    from app.interfaces import ColorsDict

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


MAIOR_60_ANOS = "Maior que 60 anos (conforme Lei 10.741/2003)"
VER_RECURSO = "Clique aqui para visualizar os recursos relacionados"
INTIMACAO_ELETRONICA = "Sistema de Citação e Intimação Eletrônica"
COLORS_DICT: ColorsDict = {
    "info": "cyan",
    "log": "yellow",
    "error": "red",
    "warning": "magenta",
    "success": "green",
}


MESSAGE = "[({pid}, {typ}, {row}, {dt})> {msg}]"
