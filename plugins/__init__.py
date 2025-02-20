"""Module for custom plugins and extensions for CrawJUD project.

Usage:
    Import your custom plugins and extensions here for use in the main application.

Example:
    >>> from .myplugin import MyPlugin

    >>> __all__ = ["MyPlugin"]

"""

from .redis_client_bot import Redis

__all__ = ["Redis"]
