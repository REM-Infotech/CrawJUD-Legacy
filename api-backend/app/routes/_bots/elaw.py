from flask import Blueprint

elaw = Blueprint("elaw", __name__, url_prefix="/elaw")


@elaw.post("/run/<int:bot_id>")
def run_bot(bot_id: int) -> str:
    return f"Running bot with ID: {bot_id}"
