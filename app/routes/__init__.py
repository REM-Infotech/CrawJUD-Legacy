from importlib import import_module

from app import app
from app.routes import handler
from app.routes.bot import bot

app.register_blueprint(bot)
import_module("app.routes.logs", __name__)

__all__ = [handler]
