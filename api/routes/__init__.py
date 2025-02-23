"""Route registration module for the CrawJUD-Bots application.

This module is responsible for dynamically importing route modules, registering blueprints,
and setting up global error handlers for the Quart application.
"""

from os import environ

from dotenv_vault import load_dotenv
from quart import Response, make_response, redirect
from werkzeug.exceptions import HTTPException

from api import app

load_dotenv()


@app.errorhandler(HTTPException)
def handle_http_exception(error: HTTPException) -> Response:
    """Handle HTTP exceptions by redirecting to a specified URL."""
    # Redirect to a specified URL in case of HTTP exceptions.
    url = environ.get("URL_WEB")
    return make_response(redirect(url))
