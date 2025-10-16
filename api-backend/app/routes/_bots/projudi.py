from flask import Blueprint

projudi = Blueprint("projudi", __name__, url_prefix="/projudi")


@projudi.post("/run/<int:bot_id>")
def run_bot(bot_id: int) -> str:
    return f"Running bot with ID: {bot_id}"
