"""Forneça funções utilitárias para formatar strings.

Este módulo contém funções para remover acentos e caracteres
especiais, tornando textos seguros para nomes de arquivos.
"""

import secrets
from datetime import datetime
from typing import TYPE_CHECKING
from unicodedata import combining, normalize

from pandas import Timestamp
from werkzeug.utils import secure_filename

if TYPE_CHECKING:
    from app.types import AnyType


def formata_string(string: str) -> str:
    """Remova acentos e caracteres especiais da string.

    Args:
        string (str): Texto a ser formatado.

    Returns:
        str: Texto formatado em caixa alta e seguro para nomes
            de arquivo.

    """
    normalized_string = "".join([
        c for c in normalize("NFKD", string) if not combining(c)
    ])

    return secure_filename(normalized_string).upper()


def random_base36() -> str:
    # Gera um número aleatório de 52 bits (mesma entropia de Math.random)
    n = secrets.randbits(52)
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    s = ""
    while n:
        n, r = divmod(n, 36)
        s = chars[r] + s
    return "0." + s or "0.0"


def normalizar(txt: str) -> str:
    return " ".join(txt.split())


def format_data(x: AnyType) -> str:
    if str(x) == "NaT" or str(x) == "nan":
        return ""

    if isinstance(x, (datetime, Timestamp)):
        return x.strftime("%d/%m/%Y")

    return x


def format_float(x: AnyType) -> str:
    return f"{x:.2f}".replace(".", ",")
