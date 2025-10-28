from flask import (
    Blueprint,
    Flask,
    Response,
    jsonify,
)
from flask_jwt_extended import jwt_required

bots = Blueprint("bots", __name__, url_prefix="/bots")


@bots.route("/listagem")
@jwt_required()
def listagem() -> Response:
    return jsonify({"data": []})


def _register_routes_bots(app: Flask) -> None:
    from .pje import pje

    app.register_blueprint(pje)
    app.register_blueprint(bots)
