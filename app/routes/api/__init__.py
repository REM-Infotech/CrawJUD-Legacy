"""Rotas globais de gerenciamento da API."""

from flask import Blueprint, Response, jsonify, make_response
from sqlalchemy import text

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/health", methods=["GET"])
def health() -> Response:
    """Endpoint do heath status.

    Returns:
        Response: JSON response indicando o status do serviço e teste de conexão com o banco de dados

    """
    from app.resources.extensions import db

    test = None
    try:
        code = 200
        test = db.session.execute(text("SELECT 1")).scalar()

    except Exception:
        code = 500

    return make_response(jsonify({"status": "ok", "db_test": test}), code)
