from flask import Response, request, send_from_directory

from app import app


def _register_routes() -> None:
    from .pje import pje

    app.register_blueprint(pje)


@app.route("/robots.txt")
def static_from_root() -> Response:
    return send_from_directory(app.static_folder, request.path[1:])  # pyright: ignore[reportArgumentType]


_register_routes()
