"""Modulo de gerenciamento de tarefas do Celery."""

from __future__ import annotations

from crawjud import bots
from crawjud.tasks import files, message

__all__ = ["bots", "files", "message"]
