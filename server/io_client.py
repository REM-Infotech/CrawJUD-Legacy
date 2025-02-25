"""Socket.IO client module for handling log events from different services.

This module sets up a Socket.IO client that listens to logging events from
various services (web, worker, beat) and prints them using tqdm.
"""

from socketio import Client
from tqdm import tqdm

io = Client()


@io.on("quart_logs_web", namespace="/quart_web")
async def quart_logs_web(data: dict[str, str]) -> None:
    """Handle logging events from the Quart web service.

    Args:
        data: Dictionary containing the log message

    """
    tqdm.write(f"{data.get('message')}")


@io.on("quart_logs", namespace="/quart")
async def quart_logs(data: dict[str, str]) -> None:
    """Handle logging events from the Quart service.

    Args:
        data: Dictionary containing the log message

    """
    tqdm.write(f"{data.get('message')}")


@io.on("worker_logs", namespace="/worker")
async def worker_logs(data: dict[str, str]) -> None:
    """Handle logging events from the worker service.

    Args:
        data: Dictionary containing the log message

    """
    tqdm.write(f"{data.get('message')}")


@io.on("beat_logs", namespace="/beat")
async def beat_logs(data: dict[str, str]) -> None:
    """Handle logging events from the beat service.

    Args:
        data: Dictionary containing the log message

    """
    tqdm.write(f"{data.get('message')}")
