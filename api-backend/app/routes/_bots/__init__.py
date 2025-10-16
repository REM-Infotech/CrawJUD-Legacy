from flask import Response, request, send_from_directory

from app import bots_app


def _register_routes() -> None:
    from ._pje import pje

    bots_app.register_blueprint(pje)


@bots_app.route("/robots.txt")
def static_from_root() -> Response:
    return send_from_directory(bots_app.static_folder, request.path[1:])  # pyright: ignore[reportArgumentType]


_register_routes()
