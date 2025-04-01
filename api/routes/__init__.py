"""Module for main application routes.

This module defines global routes, context processors, and custom error handling.
"""

import os
import re
from datetime import datetime
from traceback import format_exception

import aiofiles
import aiohttp
import httpx  # noqa: F401
import quart_flask_patch  # noqa: F401
from deep_translator import GoogleTranslator

# Quart Imports
from quart import (
    Response,
    abort,
    jsonify,
    make_response,
    send_from_directory,
)
from quart import current_app as app
from quart_jwt_extended import jwt_required
from trio import Path
from werkzeug.exceptions import HTTPException


@app.route("/", methods=["GET"])
@jwt_required
async def index() -> Response:
    """Redirect to the authentication login page.

    Returns:
        Response: A Quart redirect response to the login page.

    """
    return await make_response(jsonify(), 200)


@app.route("/favicon.png", methods=["GET"])
@jwt_required
async def serve_img() -> Response:
    """Serve the favicon image.

    Returns:
        Response: A Quart response serving the favicon.

    """
    try:
        path_icon = os.path.join(os.getcwd(), "static", "img")

        parent_path = await Path(os.getcwd())
        path_icon = parent_path.joinpath("web", "static", "img")
        path_icon = await path_icon.resolve()

        return await make_response(
            await send_from_directory(
                path_icon,
                "crawjud.png",
            ),
        )

    except Exception as e:
        err = "\n".join(format_exception(e))
        app.logger.exception(err)
        abort(500, description=f"Erro interno do servidor: {err}")


@app.route("/img/<user>.png", methods=["GET"])
@jwt_required
async def serve_profile(user: str) -> Response:
    """Serve the profile image for the specified user.

    Args:
        user (str): The user's login identifier.

    Returns:
        Response: A Quart response containing the profile image.

    """
    try:
        with app.app_context():
            from api.models import Users

            user = Users.query.filter(Users.login == user).first()
            image_data = user.blob_doc
            filename = user.filename

            if not image_data:
                url_image = "https://cdn-icons-png.flaticon.com/512/3135/3135768.png"

                async with aiohttp.ClientSession() as sess:
                    async with sess.get(url_image) as resp:
                        reponse_img = resp

                filename = os.path.basename(url_image)
                image_data = reponse_img.content

            image_data = bytes(image_data)
            filename = "".join(re.sub(r'[<>:"/\\|?*]', "_", f"{datetime.now()}_{filename}"))

            original_path = os.path.join(app.config["IMAGE_TEMP_DIR"], filename)

            with aiofiles.open(original_path, "wb") as file:
                file.write(image_data)

            response = await make_response(await send_from_directory(app.config["IMAGE_TEMP_DIR"], filename))
            response.headers["Content-Type"] = "image/png"

            return response

    except Exception as e:
        abort(500, description=f"Erro interno do servidor: {e!s}")


@app.errorhandler(HTTPException)
async def handle_http_exception(error: HTTPException) -> Response:
    """Handle HTTP exceptions and render a custom error page.

    Args:
        error (HTTPException): The raised HTTP exception.

    Returns:
        tuple: A tuple containing the rendered error page and the HTTP status code.

    """
    tradutor = GoogleTranslator(source="en", target="pt")
    name = tradutor.translate(error.name)
    desc = tradutor.translate(error.description)

    return await make_response(jsonify(name=name, description=desc), error.code)


@app.after_request
def print_response(response: Response) -> Response:
    """Log the response after the request is processed."""
    app.logger.info(f"Response: {response}")

    # response.headers["Access-Control-Allow-Origin"] = "*"
    # response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    # response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS, GET"

    return response
