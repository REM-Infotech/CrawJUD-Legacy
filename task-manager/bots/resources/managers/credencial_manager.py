"""Gerenciador de credenciais CrawJUD."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bots.head import CrawJUD


class CredencialManager:
    """Gerenciador de credenciais CrawJUD."""

    def __init__(self, bot: CrawJUD) -> None:
        """Instancia da gestão de credenciais."""
        self.bot = bot

    def load_credenciais(self, config: dict) -> None:
        self._username = config["username"]
        self._password = config["password"]

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str:
        return self._password
