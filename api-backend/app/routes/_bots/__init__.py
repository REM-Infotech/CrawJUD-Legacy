from flask import Blueprint, Flask, Response, jsonify, make_response
from flask_jwt_extended import get_current_user, jwt_required

from __types import Sistemas
from app.models import User

SISTEMAS = {"projudi", "elaw", "esaj", "pje", "jusds", "csi"}
bots = Blueprint("bots", __name__, url_prefix="/bots")


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


def _register_routes_bots(app: Flask) -> None:
    from .pje import pje
    from .projudi import projudi

    for blueprint in [projudi, pje, bots]:
        app.register_blueprint(blueprint)
