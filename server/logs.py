"""Server log handlers."""

from tqdm import tqdm

from server import io


@io.on("connect")
async def connect(sid: str, *arg: str | int, **kwargs: str | int) -> None:
    """Connect the client to the server."""
    tqdm.write(f"Client {sid} connected.")
    io.emit("connected", {"data": "Connected"})


@io.on("disconnect")
async def disconnect(sid: str, *arg: str | int, **kwargs: str | int) -> None:
    """Disconnect the client from the server."""
    tqdm.write(f"Client {sid} disconnected.")
    await io.emit("disconnected", {"data": "Disconnected"})


@io.on("system_log")
async def system_log(sid: str, *arg: str | int, **kwargs: str | int) -> None:
    """Receive and log system log messages."""
    tqdm.write(f"System log: {arg}")
    await io.emit("system_log", {"data": arg})
