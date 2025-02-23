"""Initialize the routes for the server."""

from quart import Response, make_response, render_template

from server import app


async def register_blueprint() -> None:
    """Register the ASGI, worker, and beat blueprints."""
    async with app.app_context():
        from .blueprints import asgi_, auth_, beat_, worker_

        for blueprint_ in [asgi_, worker_, beat_, auth_]:
            app.register_blueprint(blueprint_)


@app.route("/dashboard")
async def dashboard() -> Response:
    """Render the dashboard template."""
    return await make_response(await render_template("index.html", page="dashboard.html"))
