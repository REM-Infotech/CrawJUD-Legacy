"""Módulo de controle de classes de autenticação."""

from .elaw import AutenticadorElaw
from .pje import AutenticadorPJe
from .projudi import AutenticadorProjudi

__all__ = ["AutenticadorElaw", "AutenticadorPJe", "AutenticadorProjudi"]
