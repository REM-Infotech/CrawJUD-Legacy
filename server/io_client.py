"""Socket.IO client module for handling log events from different services.

This module sets up a Socket.IO client that listens to logging events from
various services (web, worker, beat) and prints them using tqdm.
"""

from typing import Any

from pynput.keyboard import Key, Listener
from socketio import Client
from tqdm import tqdm

io = Client()


def watch_input() -> bool:
    """Watch for keyboard input."""
    pressed = False

    def on_press(key: Any) -> None | bool:
        """Handle key press events."""
        nonlocal pressed

        if key == Key.esc:
            pressed = True
            return False

    with Listener(on_press=on_press) as listener:
        listener.join()

    return pressed


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
