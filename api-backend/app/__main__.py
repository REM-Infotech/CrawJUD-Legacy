"""Main Entry Point."""

from app import create_app
from app.resources.extensions import io

app = create_app()

io.run(app, host="localhost", port=5000, allow_unsafe_werkzeug=True)
