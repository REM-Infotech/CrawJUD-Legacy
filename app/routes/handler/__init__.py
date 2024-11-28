from dotenv import dotenv_values
from flask import redirect
from werkzeug.exceptions import HTTPException

from app import app


@app.errorhandler(HTTPException)
def handle_http_exception(error):

    url = dotenv_values().get("url_web")
    return redirect(url)
