"""Server log handlers."""

from tqdm import tqdm

from server import io


@io.on("connect", namespace="*")
async def connect(sid: str, *arg: str | int, **kwargs: str | int) -> None:
    """Connect the client to the server."""
    tqdm.write(f"Client {sid} connected.")
    await io.emit("connected", {"data": "Connected"})


@io.on("join", namespace="*")
async def join(sid: str, *arg: str | int, **kwargs: str | int) -> None:
    """Join the client to the server."""
    tqdm.write(f"Client {sid} joined.")
    await io.enter_room()
    await io.emit("joined", {"data": "Joined"})


@io.on("disconnect", namespace="*")
async def disconnect(sid: str, *arg: str | int, **kwargs: str | int) -> None:
    """Disconnect the client from the server."""
    tqdm.write(f"Client {sid} disconnected.")
    await io.emit("disconnected", {"data": "Disconnected"})


@io.on("application_logs", namespace="/application_logs")
async def system_log(sid: str, *arg: str | int, **kwargs: str | int) -> None:
    """Receive and log system log messages."""
    tqdm.write(f"System log: {arg}")
    await io.emit("system_log", {"data": arg})


@io.on("quart_logs", namespace="/quart")
async def quart_logs(sid: str, *arg: str | int, **kwargs: str | int) -> None:
    """Receive and log Quart log messages."""
    tqdm.write(f"Quart log: {arg}")
    await io.emit("quart_logs", {"data": arg})


@io.on("worker_logs", namespace="/worker")
async def worker_logs(sid: str, *arg: str | int, **kwargs: str | int) -> None:
    """Receive and log worker log messages."""
    tqdm.write(f"Worker log: {arg}")
    await io.emit("worker_logs", {"data": arg})


@io.on("beat_logs", namespace="/beat")
async def beat_logs(sid: str, *arg: str | int, **kwargs: str | int) -> None:
    """Receive and log beat log messages."""
    tqdm.write(f"Beat log: {arg}")
    await io.emit("beat_logs", {"data": arg})
