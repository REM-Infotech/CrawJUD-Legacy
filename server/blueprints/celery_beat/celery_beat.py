"""Blueprint for the Celery Beat server."""

from pathlib import Path

from quart import Blueprint, Response, make_response, render_template

template_folder = Path(__file__).parent.resolve().joinpath("templates")
static_folder = Path(__file__).parent.resolve().joinpath("static")
beat_ = Blueprint(
    "beat",
    __name__,
    template_folder=str(template_folder),
    static_folder=str(static_folder),
    url_prefix="/beat",
)


@beat_.get("/status")
async def status() -> Response:
    """Check the status of the beat server."""
    return await make_response(render_template("index.html", page="status.html"))


@beat_.post("/shutdown")
async def shutdown() -> Response:
    """Shutdown the beat server."""
    return await make_response(render_template("index.html", page="shutdown.html"))


@beat_.get("/restart")
async def restart() -> Response:
    """Restart the beat server."""
    return await make_response(render_template("index.html", page="restart.html"))


@beat_.get("/start")
async def start() -> Response:
    """Start the beat server."""
    return await make_response(render_template("index.html", page="start.html"))
