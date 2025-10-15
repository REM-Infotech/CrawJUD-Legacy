"""Module for authentication routes.

This module defines the authentication-related routes for the API, including
    user login, logout, and token refresh functionality.
    It utilizes Quart for asynchronous HTTP handling and flask_jwt_extended for
    JWT-based authentication. The module provides endpoints
    for user authentication, session management, and secure token handling.

Routes:
    /login (GET, POST, OPTIONS): Authenticates a user and issues JWT tokens.
    /logout (POST): Logs out the current user and clears JWT cookies.
    /refresh (POST): Refreshes the access token using a valid refresh token.
Classes:
    LoginForm: Dataclass representing the structure of the login form data.
Dependencies:
    - Quart
    - flask_jwt_extended
    - SQLAlchemy (for database access)
    - api.models.users (for user and token blocklist models)

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import jwt
from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    jsonify,
    make_response,
    request,
)
from flask_jwt_extended import (
    create_access_token,
    unset_jwt_cookies,
)
from flask_sqlalchemy import SQLAlchemy

from app.models import User

if TYPE_CHECKING:
    pass


auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.post("/login")
def login() -> Response:
    """Authenticate the user and start a session.

    Returns:
        Response: HTTP response redirecting on success or rendering
            the login template.

    """
    db: SQLAlchemy = current_app.extensions["sqlalchemy"]
    data = request.get_json(force=True)  # força o parsing do JSON

    # Verifica se os campos obrigatórios estão presentes
    if not data or not data.get("login") or not data.get("password"):
        abort(400, description="Login e senha são obrigatórios.")

    authenticated = User.authenticate(data["login"], data["password"])
    if not authenticated:
        abort(401, description="Credenciais inválidas.")

    user = db.session.query(User).filter_by(login=data["login"]).first()
    if not user:
        abort(404, description="Usuário não encontrado.")

    response = make_response(
        jsonify(message="Login efetuado com sucesso!"), 200
    )
    access_token = create_access_token(identity=user.id)

    decoded_token = jwt.decode(
        access_token, options={"verify_signature": False}
    )

    response.set_cookie(
        current_app.config["JWT_ACCESS_COOKIE_NAME"],
        value=access_token,
        max_age=3600 * 24 * 7,
        secure=current_app.config["JWT_COOKIE_SECURE"],
        httponly=True,
        domain=current_app.config["SERVER_NAME"],
        path=current_app.config["JWT_ACCESS_COOKIE_PATH"],
        samesite=current_app.config["JWT_COOKIE_SAMESITE"],
    )
    response.set_cookie(
        current_app.config["JWT_ACCESS_CSRF_COOKIE_NAME"],
        value=decoded_token["csrf"],
        max_age=3600 * 24 * 7,
        secure=current_app.config["JWT_COOKIE_SECURE"],
        httponly=False,
        domain=current_app.config["SERVER_NAME"],
        path="/",
        samesite=current_app.config["JWT_COOKIE_SAMESITE"],
    )

    return response


@auth.route("/logout", methods=["POST"])
def logout() -> Response:
    """Log out the current user and clear session cookies.

    Returns:
        Response: Redirect response to the login page.

    """
    response = make_response(jsonify(message="Logout efetuado com sucesso!"))
    unset_jwt_cookies(response)
    return response
