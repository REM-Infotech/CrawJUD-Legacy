"""Decora classes e métodos relacionados ao bot para integração com Socket.IO.

Este módulo fornece:
- wrap_init: decora o método __init__ para exibir informações de instanciação;
- wrap_cls: decora classes bot para execução sob controle de conexão Socket.IO.
"""

from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from crawjud.controllers.master import CrawJUD


def wrap_init[T](cls: type[CrawJUD]) -> type[T]:
    """Decora o método __init__ de uma classe para exibir informações de instancia.

    Args:
        cls (type[CrawJUD]): Classe do bot a ser decorada.

    Returns:
        type[T]: Classe decorada com __init__ modificado.

    """
    original_init = cls.__init__

    @wraps(original_init)
    def novo_init(
        self: T = None,
        *args: T,
        **kwargs: T,
    ) -> None:
        return original_init(self, *args, **kwargs)

    cls.__init__ = novo_init
    return cls


def wrap_cls[T](cls: type[CrawJUD]) -> type[T]:
    """Decora uma classe bot para executar métodos sob controle de conexão Socket.IO.

    Args:
        cls (T): Classe do bot a ser decorada.

    Returns:
        type[T]: Classe decorada com execução controlada via Socket.IO.

    """
    original_cls = cls

    @wraps(wrap_cls)
    def novo_init(
        self: T | None = None,
        *args: T,
        **kwargs: T,
    ) -> None:
        cls = original_cls(current_task=self, *args, **kwargs)
        return cls.execution()

    return novo_init
