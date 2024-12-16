from importlib import import_module

from app import app

from ..routes import handler
from ..routes.bot import bot
from ..routes.webhook import wh

app.register_blueprint(wh)
app.register_blueprint(bot)
import_module("app.routes.logs", __name__)

__all__ = [handler]
