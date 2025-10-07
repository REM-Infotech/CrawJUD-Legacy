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

import json
from dataclasses import dataclass
from datetime import datetime
from traceback import format_exception
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    jsonify,
    make_response,
    request,
    session,
)
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
)

from app.models.users import TokenBlocklist as TokenBlocklist
from app.models.users import Users

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy


auth = Blueprint("auth", __name__)

usr = None


@dataclass
class LoginForm:
    """Represents the data required for user login.

    Attributes:
        login (str): The user's login identifier (e.g., username or email).
        password (str): The user's password.
        remember_me (bool): Indicates whether the user should remain
            logged in across sessions.

    """

    """Dataclass for the login form."""

    login: str
    password: str
    remember_me: bool


@auth.post("/login")
def login() -> Response:
    """Authenticate the user and start a session.

    Returns:
        Response: HTTP response redirecting on success or rendering
            the login template.

    """
    try:
        db: SQLAlchemy = current_app.extensions["sqlalchemy"]
        request_json: dict[str, str] = (
            request.json or request.form or request.data
        )
        if request.method == "OPTIONS":
            return make_response(jsonify({"message": "OK"}), 200)

        if isinstance(request_json, bytes):
            request_json = json.loads(request_json.decode("utf-8"))

        if not request_json:
            return make_response(
                jsonify({"message": "Erro ao efetuar login!"}),
                400,
            )

        username = request_json.get("login", request_json.get("email"))
        password = request_json.get("password")
        remember = request_json.get("remember_me")
        form = LoginForm(username, password, remember)

        from sqlalchemy import or_

        usr = (
            db.session.query(Users)
            .filter(or_(Users.login == form.login, Users.email == form.login))
            .first()
        )
        if usr and usr.check_password(form.password):
            is_admin = bool(usr.admin or usr.supersu)

            usr.login_time = datetime.now(tz=ZoneInfo("America/Manaus"))
            db.session.commit()

            resp = make_response(
                jsonify({
                    "message": "Login Efetuado com sucesso!",
                    "isAdmin": is_admin,
                }),
                200,
            )

            access_token = create_access_token(identity=usr)
            set_access_cookies(resp, access_token)

            session.permanent = remember

            return resp

        if not usr or not usr.check_password(form.password):
            resp = jsonify({"message": "Usuário ou senha incorretos!"})
            resp.status_code = 401
            resp.headers = {"Content-Type": "application/json"}
            return resp

    except ValueError as e:
        abort(500, description="\n".join(format_exception(e)))


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
