"""Module for main application routes.

This module defines global routes, context processors, and custom error handling.
"""

import datetime
import json
import os
import re
import traceback
from typing import Any

import httpx
from deep_translator import GoogleTranslator
from flask_login import current_user, login_required

# Quart Imports
from quart import (
    Response,
    abort,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from quart import current_app as app
from werkzeug.exceptions import HTTPException
from werkzeug.local import LocalProxy


@app.context_processor
def inject_user_cookies() -> dict[str, str | LocalProxy[Any | None] | None]:
    """Inject user-related cookies and authentication data into the template context.

    Returns:
        dict: A dictionary containing cookies and current user information.

    """
    admin_cookie, supersu_cookie = None, None

    if current_user.is_authenticated:
        if session.get("_id"):
            admin_cookie = request.cookies.get("roles_admin")
            if admin_cookie:
                if json.loads(admin_cookie).get("login_id") != session["_id"]:
                    admin_cookie = None

                supersu_cookie = request.cookies.get("roles_supersu")
                if supersu_cookie:
                    if json.loads(supersu_cookie).get("login_id") != session["_id"]:
                        supersu_cookie = None

    return {
        "admin_cookie": admin_cookie,
        "supersu_cookie": supersu_cookie,
        "current_user": current_user,
    }


@app.route("/", methods=["GET"])
def index() -> Response:
    """Redirect to the authentication login page.

    Returns:
        Response: A Quart redirect response to the login page.

    """
    return make_response(redirect(url_for("auth.login")), 302)


@app.route("/favicon.png", methods=["GET"])
def serve_img() -> Response:
    """Serve the favicon image.

    Returns:
        Response: A Quart response serving the favicon.

    """
    try:
        paht_icon = os.path.join(os.getcwd(), "static", "img")
        url = make_response(send_from_directory(paht_icon, "crawjud.png"))
        return url

    except Exception:
        err = traceback.format_exc()
        app.logger.exception(err)
        abort(500, description=f"Erro interno do servidor: {err}")


@app.route("/img/<user>.png", methods=["GET"])
@login_required
def serve_profile(user: str) -> Response:
    """Serve the profile image for the specified user.

    Args:
        user (str): The user's login identifier.

    Returns:
        Response: A Quart response containing the profile image.

    """
    try:
        with app.app_context():
            from web.models import Users

            user = Users.query.filter(Users.login == user).first()
            image_data = user.blob_doc
            filename = user.filename

            if not image_data:
                url_image = "https://cdn-icons-png.flaticon.com/512/3135/3135768.png"
                reponse_img = httpx.get(url_image)

                filename = os.path.basename(url_image)
                image_data = reponse_img.content

            image_data = bytes(image_data)
            filename = "".join(re.sub(r'[<>:"/\\|?*]', "_", f"{datetime.datetime.now()}_{filename}"))

            original_path = os.path.join(app.config["IMAGE_TEMP_DIR"], filename)

            with open(original_path, "wb") as file:
                file.write(image_data)

            response = make_response(send_from_directory(app.config["IMAGE_TEMP_DIR"], filename))
            response.headers["Content-Type"] = "image/png"

            return response

    except Exception as e:
        abort(500, description=f"Erro interno do servidor: {e!s}")


@app.errorhandler(HTTPException)
def handle_http_exception(error: HTTPException) -> Response:
    """Handle HTTP exceptions and render a custom error page.

    Args:
        error (HTTPException): The raised HTTP exception.

    Returns:
        tuple: A tuple containing the rendered error page and the HTTP status code.

    """
    tradutor = GoogleTranslator(source="en", target="pt")
    name = tradutor.translate(error.name)
    desc = tradutor.translate(error.description)

    return make_response(
        render_template("handler/index.html", name=name, desc=desc, code=error.code),
        error.code,
    )
