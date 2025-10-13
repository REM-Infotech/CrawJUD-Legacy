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

from traceback import format_exception
from typing import TYPE_CHECKING, cast

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
    set_access_cookies,
    unset_jwt_cookies,
)
from flask_sqlalchemy import SQLAlchemy

from app._types import LoginForm
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
    response: Response = make_response(jsonify(message="responsta vazia"), 201)

    try:
        db: SQLAlchemy = current_app.extensions["sqlalchemy"]
        data = cast(LoginForm, request.get_json())

        if not data.get("login") or not data.get("password"):
            abort(400, description="Login e senha são obrigatórios.")

        authenticated = User.authenticate(data["login"], data["password"])
        if not authenticated:
            abort(401, description="Credenciais inválidas.")

        user = db.session.query(User).filter_by(login=data["login"]).first()
        response = make_response(
            jsonify(message="Login efetuado com sucesso!"),
        )
        access_token = create_access_token(identity=user)

        set_access_cookies(response, access_token)

    except ValueError as e:
        abort(500, description="\n".join(format_exception(e)))

    return response


@auth.route("/logout", methods=["POST"])
def logout() -> Response:
    """Log out the current user and clear session cookies.

    Returns:
        Response: Redirect response to the login page.

    """
    response = make_response(jsonify(msg="Logout efetuado com sucesso!"))
    try:
        unset_jwt_cookies(response)

    except ValueError as e:
        abort(500, description="\n".join(format_exception(e)))

    return response
