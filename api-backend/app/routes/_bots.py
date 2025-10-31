import json
from uuid import uuid4

from flask import (
    Blueprint,
    Response,
    jsonify,
    make_response,
    request,
)
from flask_jwt_extended import get_current_user, jwt_required

from __types import Dict, Sistemas
from app._forms.head import FormBot
from app.decorators import CrossDomain
from app.models import User
from constants import SISTEMAS

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
        code = 201
        try:
            request_data: Dict = json.loads(request.get_data())
            data = {
                k: v
                for k, v in list(request_data.items())
                if k != "configuracao_form"
            }

            form = FormBot.load_form(
                request_data["configuracao_form"], data
            )
            _dict_form = form.to_dict()

            payload = {
                "title": "Sucesso",
                "message": "Robô inicializado com sucesso!",
                "status": "success",
                "pid": uuid4().hex[:6].upper(),
            }
            code = 200

        except Exception as e:
            print(e)

    return make_response(jsonify(payload), code)
