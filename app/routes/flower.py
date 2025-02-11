"""Flower proxy."""

import aiohttp
from quart import Blueprint, Response, request
from quart import current_app as app

worker_celery = Blueprint("worker_celery", __name__)


# Configuração do Flower
FLOWER_URL = "http://localhost:5555"  # Mude a porta se necessário


# Proxy para o Flower
@app.route("/<path:path>", methods=["GET", "POST", "DELETE", "PUT"])
async def proxy(path: str) -> Response:
    """Proxy for Flower."""
    async with aiohttp.ClientSession() as session:
        url = f"{FLOWER_URL}/{path}"
        async with session.request(
            request.method,
            url,
            data=await request.data,
            headers={k: v for k, v in request.headers.items() if k != "Host"},
        ) as resp:
            body = await resp.read()
            return Response(body, status=resp.status, headers=dict(resp.headers))
