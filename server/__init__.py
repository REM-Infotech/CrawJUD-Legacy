"""Module for manage application with System Status and System Information."""

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path

from quart import Quart, Response, make_response, render_template
from socketio import ASGIApp, AsyncServer

instance_dir = Path(__file__).parent.resolve().joinpath("instance")
template_dir = Path(__file__).parent.resolve().joinpath("templates")
static_dir = Path(__file__).parent.resolve().joinpath("static")

running_servers = {}

app = Quart(
    __name__,
    template_folder=str(template_dir),
    static_folder=str(static_dir),
    instance_path=str(instance_dir),
)

io = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_interval=25,
    ping_timeout=10,
)

import_module("server.logs", __package__)


@dataclass
class StoreProcess:
    """Dataclass for storing process information."""

    process_name: str
    process_id: int
    process_status: str
    process_object: object


@app.route("/dashboard")
async def dashboard() -> Response:
    """Render the dashboard template."""
    return await make_response(await render_template("index.html", page="dashboard.html"))


async def register_blueprint() -> None:
    """Register the ASGI, worker, and beat blueprints."""
    async with app.app_context():
        from .blueprints import asgi_, beat_, worker_

        for blueprint_ in [asgi_, worker_, beat_]:
            app.register_blueprint(blueprint_)


async def create_app() -> Quart:
    """Create and configure the Quart application."""
    await register_blueprint()
    return ASGIApp(io, app)
