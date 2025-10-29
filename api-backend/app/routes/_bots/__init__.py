from flask import Blueprint, Flask, Response, jsonify, make_response
from flask_jwt_extended import get_current_user, jwt_required

bots = Blueprint("bots", __name__, url_prefix="/bots")


@bots.route("/listagem")
@jwt_required()
def listagem() -> Response:
    from app.models import User

    user: User = get_current_user()

    return make_response(
        jsonify({
            "listagem": [
                {
                    "id": bot.Id,
                    "display_name": bot.display_name,
                    "sistema": bot.sistema,
                    "categoria": bot.categoria,
                    "descricao": bot.descricao,
                }
                for bot in user.license_.bots
            ]
        }),
        200,
    )


def _register_routes_bots(app: Flask) -> None:
    from .pje import pje
    from .projudi import projudi

    for blueprint in [projudi, pje, bots]:
        app.register_blueprint(blueprint)
