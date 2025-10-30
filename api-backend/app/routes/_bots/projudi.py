from uuid import uuid4

from flask import Blueprint, Response, jsonify, make_response, request
from flask_jwt_extended import get_current_user, jwt_required

from app.decorators import CrossDomain
from app.models import User

projudi = Blueprint("projudi", __name__, url_prefix="/bot/projudi")


@projudi.post("/run")
@CrossDomain(origin="*", methods=["get", "post", "options"])
@jwt_required()
def run_bot() -> Response:
    _request = request
    return make_response(
        jsonify({
            "title": "Sucesso",
            "message": "Robô inicializado com sucesso!",
            "status": "success",
            "pid": uuid4().hex[:6].upper(),
        })
    )


@projudi.get("/credenciais")
@jwt_required()
def provide_credentials() -> Response:
    user: User = get_current_user()

    lic = user.license_

    list_credentials = [
        {"value": credential.Id, "text": credential.nome_credencial}
        for credential in list(
            filter(
                lambda credential: credential.sistema == "PROJUDI",
                lic.credenciais,
            )
        )
    ]

    return make_response(jsonify({"credenciais": list_credentials}), 200)
