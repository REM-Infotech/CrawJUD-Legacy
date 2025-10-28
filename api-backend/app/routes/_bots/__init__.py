import json
from pathlib import Path

from flask import (
    Blueprint,
    Flask,
    Response,
    jsonify,
    make_response,
)
from flask_jwt_extended import jwt_required

bots = Blueprint("bots", __name__, url_prefix="/bots")


@bots.route("/listagem")
@jwt_required()
def listagem() -> Response:
    file_path = Path(__file__).cwd().joinpath("app", "export.json")
    data = {"listagem": []}
    code = 201
    if file_path.exists():
        code = 200
        with file_path.open("r", encoding="utf-8") as f:
            data.update({"listagem": json.load(f)})

    return make_response(jsonify(data), code)


def _register_routes_bots(app: Flask) -> None:
    from .pje import pje

    app.register_blueprint(pje)
    app.register_blueprint(bots)
