"""Main module for the server."""

import asyncio

import uvicorn

from . import create_app

if __name__ == "__main__":
    app = asyncio.run(create_app())
    hostname = "127.0.0.1"
    port = 7000
    uvicorn.run(
        app,
        host=hostname,
        port=port,
    )
