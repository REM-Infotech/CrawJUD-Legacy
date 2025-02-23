"""Main module for the server."""

import asyncio
from os import environ

import uvicorn

from . import create_app

if __name__ == "__main__":
    environ.update({
        "SERVER_MANAGEMENT": "True",
    })
    app = asyncio.run(create_app())
    hostname = "127.0.0.1"
    port = 7000
    uvicorn.run(
        app,
        host=hostname,
        port=port,
    )
