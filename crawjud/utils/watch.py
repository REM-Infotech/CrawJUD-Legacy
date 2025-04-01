"""Socket.IO client module for handling log events from different services.

This module sets up a Socket.IO client that listens to logging events from
various services (web, worker, beat) and prints them using tqdm.
"""

from os import getcwd
from pathlib import Path
from threading import Event, Thread
from typing import Any

import tailer
from pynput.keyboard import Key, Listener
from tqdm import tqdm


def watch_input(stop_event: Event) -> None:
    """Escuta a tecla ESC e ativa o evento de parada."""

    def on_press(key: Any) -> None:
        if key == Key.esc:
            stop_event.set()
            return False  # Para o listener

    with Listener(on_press=on_press) as listener:
        listener.join()


def monitor_log(file_name: str = None, file_path: Path = None) -> None:
    """Monitora um arquivo de log usando tailer e para quando ESC for pressionado."""
    stop_event = Event()

    if not file_path:
        file_path = Path(getcwd()).joinpath("logs", file_name)

    if not isinstance(file_path, Path):
        raise ValueError("file_path must be a pathlib.Path object.")

    # Inicia a thread para capturar entrada do teclado
    Thread(target=watch_input, args=(stop_event,), daemon=True).start()

    # Função para rodar tailer.follow() em uma thread separada
    def tailer_thread() -> None:
        with file_path.open() as f:
            for line in tailer.follow(f):
                if stop_event.is_set():
                    break
                tqdm.write(line.strip())

    # Inicia a thread do tailer
    t = Thread(target=tailer_thread, daemon=True)
    t.start()

    # Aguarda a tecla ESC ser pressionada
    stop_event.wait()
