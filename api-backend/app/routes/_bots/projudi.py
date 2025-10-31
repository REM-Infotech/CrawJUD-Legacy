import json
from uuid import uuid4

from flask import Blueprint, Response, jsonify, make_response, request
from flask_jwt_extended import jwt_required

from app.decorators import CrossDomain

projudi = Blueprint("projudi", __name__, url_prefix="/bot/projudi")


@projudi.post("/run")
@CrossDomain(origin="*", methods=["get", "post", "options"])
@jwt_required()
def run_bot() -> Response:
    _data = json.loads(request.get_data())

    return make_response(
        jsonify({
            "title": "Sucesso",
            "message": "Robô inicializado com sucesso!",
            "status": "success",
            "pid": uuid4().hex[:6].upper(),
        })
    )
