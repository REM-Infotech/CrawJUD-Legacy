"""Server log handlers."""

from typing import Any

from tqdm import tqdm

from server import io


@io.on("connect", namespace="*")
async def connect(
    namespace: str = "/",
    sid: str = None,
    header: dict[str, Any] = None,
    data: dict[str, str] = None,
    **kwargs: str | int,
) -> None:
    """Connect the client to the server."""
    # data_kwargs = kwargs  # noqa: F841
    # data_args = args  # noqa: F841
    tqdm.write(f"Client {sid} connected.")
    await io.emit("connected", {"message": "Connected"})


@io.on("join", namespace="*")
async def join(
    namespace: str = "/",
    sid: str = None,
    header: dict[str, Any] = None,
    data: dict[str, str] = None,
    **kwargs: str | int,
) -> None:
    """Join the client to the server."""
    tqdm.write(f"Client {sid} joined.")
    await io.enter_room()
    await io.emit("joined", {"message": "Joined"})


@io.on("disconnect", namespace="*")
async def disconnect(
    namespace: str = "/",
    sid: str = None,
    header: dict[str, Any] = None,
    data: dict[str, str] = None,
    **kwargs: str | int,
) -> None:
    """Disconnect the client from the server."""
    tqdm.write(f"Client {sid} disconnected.")
    await io.emit("disconnected", {"message": "Disconnected"})


@io.on("application_logs", namespace="/application_logs")
async def system_log(
    sid: str = None,
    data: dict[str, str] = None,
    **kwargs: str | int,
) -> None:
    """Receive and log system log messages."""
    message = data.get("message")
    tqdm.write(f"System log: {message}")
    await io.emit("system_log", {"message": message}, namespace="/application_logs")


@io.on("quart_logs", namespace="/quart")
async def quart_logs(
    sid: str = None,
    data: dict[str, str] = None,
    **kwargs: str | int,
) -> None:
    """Receive and log Quart log messages."""
    message = data.get("message")
    await io.emit("quart_logs", {"message": message}, namespace="/quart")


@io.on("worker_logs", namespace="/worker")
async def worker_logs(
    sid: str = None,
    data: dict[str, str] = None,
    **kwargs: str | int,
) -> None:
    """Receive and log worker log messages."""
    message = data.get("message")
    tqdm.write(f"Worker log: {message}")
    await io.emit("worker_logs", {"message": message}, namespace="/worker")


@io.on("beat_logs", namespace="/beat")
async def beat_logs(
    sid: str = None,
    data: dict[str, str] = None,
    **kwargs: str | int,
) -> None:
    """Receive and log beat log messages."""
    message = data.get("message")
    tqdm.write(f"Beat log: {message}")
    await io.emit("beat_logs", {"message": message}, namespace="/beat")
