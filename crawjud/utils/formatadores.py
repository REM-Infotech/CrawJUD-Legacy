"""Fornece funções utilitárias para formatação dados."""

from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo


def formata_tempo[T](item: T) -> T | datetime:
    """Formata datas e horas em string para objetos datetime conforme padrões ISO 8601.

    Args:
        item (T): Valor a ser formatado, podendo ser string ou outro tipo.

    Returns:
        T | datetime: Retorna datetime se o item for string compatível, senão retorna o original.

    """
    # Verifica se o item é uma string e tenta converter para datetime
    if isinstance(item, str):
        if re.match(
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$",
            item.split(".")[0],
        ):
            return datetime.strptime(
                item.split(".")[0],
                "%Y-%m-%dT%H:%M:%S",
            ).replace(
                tzinfo=ZoneInfo("America/Manaus"),
            )

        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}$", item):
            return datetime.strptime(item, "%Y-%m-%dT%H:%M:%S.%f").replace(
                tzinfo=ZoneInfo("America/Manaus"),
            )

    return item
