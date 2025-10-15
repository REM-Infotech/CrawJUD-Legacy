"""Main Entry Point."""

import uvicorn
from asgiref.wsgi import WsgiToAsgi

from app import create_app

app = WsgiToAsgi(create_app())

uvicorn.run(app, host="127.0.0.1", port=5000)
