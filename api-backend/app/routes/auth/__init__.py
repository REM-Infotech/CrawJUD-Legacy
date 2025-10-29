"""Módulo de controle das rotas de autenticação da API."""

import traceback

from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    jsonify,
    make_response,
    request,
)
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
)
from flask_sqlalchemy import SQLAlchemy

from app.models import User

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.post("/login")
def login() -> Response:
    """Rota de autenticação da api.

    Returns:
        Response: Response da autenticação

    """
    response = {}
    try:
        db: SQLAlchemy = current_app.extensions["sqlalchemy"]
        data = request.get_json(force=True)  # força o parsing do JSON

        # Verifica se os campos obrigatórios estão presentes
        if not data or not data.get("login") or not data.get("password"):
            abort(400, description="Login e senha são obrigatórios.")

        authenticated = User.authenticate(data["login"], data["password"])
        if not authenticated:
            abort(401, description="Credenciais inválidas.")

        user = db.session.query(User).filter_by(login=data["login"]).first()
        if not user:
            abort(404, description="Usuário não encontrado.")

        response = make_response(
            jsonify(message="Login efetuado com sucesso!"), 200
        )
        access_token = create_access_token(identity=str(user.Id))

        set_access_cookies(response=response, encoded_access_token=access_token)

    except Exception as e:
        _exc = traceback.format_exception(e)

    return response


@auth.route("/logout", methods=["POST"])
def logout() -> Response:
    """Rota de logout.

    Returns:
        Response: Response do logout.

    """
    response = make_response(jsonify(message="Logout efetuado com sucesso!"))
    unset_jwt_cookies(response)
    return response
