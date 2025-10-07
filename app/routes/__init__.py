from flask import Response, make_response, redirect, url_for
from flask import current_app as app

from ._config import register_routes

__all__ = ["register_routes"]


@app.route("/", methods=["GET"])
def index() -> Response:
    return make_response(redirect(url_for("api.health")))
