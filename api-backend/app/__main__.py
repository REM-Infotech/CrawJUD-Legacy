"""Main Entry Point."""

import importlib

from flask_socketio import SocketIO

from app import create_app

app = create_app()

io: SocketIO = app.extensions["socketio"]
importlib.import_module("app.routes", __package__)

io.run(app, host="localhost", port=5000, allow_unsafe_werkzeug=True)
