from flask import Blueprint

pje = Blueprint("pje", __name__, url_prefix="/pje")


@pje.post("/run/<int:bot_id>")
def run_bot(bot_id: int) -> str:
    return f"Running bot with ID: {bot_id}"
