from flask import Blueprint, Response, current_app, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy

from app.models._bot import Bots

bot = Blueprint("bot", __name__, url_prefix="/bot")


@bot.get("/listagem")
def listagem() -> Response:
    """Listagem de bots.

    Returns:
        Response: response da listagem

    """
    return make_response(jsonify(data=[{}]))


@bot.post("/bot/start/<int:id>")
def bot_start(Id: int) -> Response:  # noqa: N803
    db: SQLAlchemy = current_app.extensions["sqlalchemy"]
    bot = db.session.query(Bots).filter(Bots.Id == Id).first()

    if bot:
        return make_response(jsonify(message="Robô inicializado"))

    return make_response(jsonify(message="Falha ao iniciar robô"), 201)
