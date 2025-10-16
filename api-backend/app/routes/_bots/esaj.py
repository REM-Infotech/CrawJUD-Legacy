from flask import Blueprint

esaj = Blueprint("esaj", __name__, url_prefix="/esaj")


@esaj.post("/run/<int:bot_id>")
def run_bot(bot_id: int) -> str:
    return f"Running bot with ID: {bot_id}"
