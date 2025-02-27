"""CrawJUD Manager Package."""

from .menu import MenuManager
from .runner import RunnerServices


class HeadCrawjudManager(MenuManager, RunnerServices):
    """Head class for CrawJUDManager."""
