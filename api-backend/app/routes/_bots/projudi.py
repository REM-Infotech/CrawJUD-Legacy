from flask import Blueprint, Response, jsonify, make_response
from flask_jwt_extended import get_current_user, jwt_required

from app.models import User

projudi = Blueprint("projudi", __name__, url_prefix="/bot/projudi")


@projudi.post("/run/<int:bot_id>")
@jwt_required
def run_bot(bot_id: int) -> str:
    return f"Running bot with ID: {bot_id}"


@projudi.get("/credenciais")
@jwt_required()
def provide_credentials() -> Response:
    user: User = get_current_user()

    lic = user.license_

    list_credentials = [
        {"value": credential.Id, "text": credential.nome_credencial}
        for credential in list(
            filter(
                lambda credential: credential.system == "projudi",
                lic.credenciais,
            )
        )
    ]

    return make_response(jsonify({"credenciais": list_credentials}), 200)
