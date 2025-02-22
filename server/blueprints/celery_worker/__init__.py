"""Blueprint for the worker server."""

from pathlib import Path

from quart import Blueprint, Response, make_response, render_template

template_folder = Path(__file__).parent.resolve().joinpath("templates")
static_folder = Path(__file__).parent.resolve().joinpath("static")
worker_ = Blueprint(
    "worker",
    __name__,
    template_folder=str(template_folder),
    static_folder=str(static_folder),
    url_prefix="/worker",
)


@worker_.get("/status")
async def status() -> Response:
    """Check the status of the worker server."""
    return await make_response(render_template("index.html", page="status.html"))


@worker_.post("/shutdown")
async def shutdown() -> Response:
    """Shutdown the worker server."""
    return await make_response(render_template("index.html", page="shutdown.html"))


@worker_.get("/restart")
async def restart() -> Response:
    """Restart the worker server."""
    return await make_response(render_template("index.html", page="restart.html"))


@worker_.get("/start")
async def start() -> Response:
    """Start the worker server."""
    return await make_response(render_template("index.html", page="start.html"))
