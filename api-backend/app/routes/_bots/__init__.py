import json
from uuid import uuid4

from flask import (
    Blueprint,
    Flask,
    Response,
    jsonify,
    make_response,
    request,
)
from flask_jwt_extended import get_current_user, jwt_required

from __types import Sistemas
from app.decorators import CrossDomain
from app.models import User

SISTEMAS = {"projudi", "elaw", "esaj", "pje", "jusds", "csi"}
bots = Blueprint("bots", __name__, url_prefix="/bot")


def is_sistema(valor: Sistemas) -> bool:
    return valor in SISTEMAS


@bots.route("/listagem")
@jwt_required()
def listagem() -> Response:
    user: User = get_current_user()

    return make_response(
        jsonify({
            "listagem": [
                {
                    "Id": bot.Id,
                    "display_name": bot.display_name,
                    "sistema": bot.sistema,
                    "categoria": bot.categoria,
                    "configuracao_form": bot.configuracao_form,
                    "descricao": bot.descricao,
                }
                for bot in user.license_.bots
            ]
        }),
        200,
    )


@bots.get("/<string:sistema>/credenciais")
@jwt_required()
def provide_credentials(sistema: Sistemas) -> Response:
    list_credentials = []
    if is_sistema(sistema):
        system = sistema.upper()
        user: User = get_current_user()

        lic = user.license_

        list_credentials.extend([
            {"value": credential.Id, "text": credential.nome_credencial}
            for credential in list(
                filter(
                    lambda credential: credential.sistema == system,
                    lic.credenciais,
                )
            )
        ])

    return make_response(
        jsonify({"credenciais": list_credentials}), 200
    )


@bots.post("/<string:sistema>/run")
@CrossDomain(origin="*", methods=["get", "post", "options"])
@jwt_required()
def run_bot(sistema: Sistemas) -> Response:
    payload = {
        "title": "Erro",
        "message": "Erro ao iniciar robô",
        "status": "error",
    }

    if is_sistema(sistema):
        _data = json.loads(request.get_data())
        payload = {
            "title": "Sucesso",
            "message": "Robô inicializado com sucesso!",
            "status": "success",
            "pid": uuid4().hex[:6].upper(),
        }

    return make_response(jsonify(payload), 201)


def _register_routes_bots(app: Flask) -> None:
    app.register_blueprint(bots)
