"""ASGI blueprint for the server."""

from pathlib import Path

from quart import Blueprint, Response, make_response, render_template

template_folder = Path(__file__).parent.resolve().joinpath("templates")
static_folder = Path(__file__).parent.resolve().joinpath("static")
asgi_ = Blueprint(
    "asgi",
    __name__,
    template_folder=str(template_folder),
    static_folder=str(static_folder),
    url_prefix="/asgi",
)


@asgi_.get("/status")
async def status() -> Response:
    """Check the status of the ASGI server."""
    return await make_response(render_template("index.html", page="status.html"))


@asgi_.post("/shutdown")
async def shutdown() -> Response:
    """Shutdown the ASGI server."""
    return await make_response(render_template("index.html", page="shutdown.html"))


@asgi_.get("/restart")
async def restart() -> Response:
    """Restart the ASGI server."""
    return await make_response(render_template("index.html", page="restart.html"))


@asgi_.get("/start")
async def start() -> Response:
    """Start the ASGI server."""
    return await make_response(render_template("index.html", page="start.html"))
