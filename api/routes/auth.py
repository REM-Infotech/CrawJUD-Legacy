"""Module for authentication routes."""

import os
import pathlib
from dataclasses import dataclass
from traceback import format_exception

import rich
from flask_sqlalchemy import SQLAlchemy
from quart import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    make_response,
    request,
)
from quart_jwt_extended import (  # noqa: F401
    create_access_token,
    create_refresh_token,
    decode_token,
    get_csrf_token,
    get_jwt_identity,
    jwt_refresh_token_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)

from api.models.users import TokenBlocklist as TokenBlocklist
from api.models.users import Users

path_template = os.path.join(pathlib.Path(__file__).parent.resolve(), "templates")
auth = Blueprint("auth", __name__, template_folder=path_template)

usr = None


@dataclass
class LoginForm:
    """Dataclass for the login form."""

    login: str
    password: str
    remember_me: bool


@auth.route("/login", methods=["GET", "POST", "OPTIONS"])
async def login() -> Response:
    """Authenticate the user and start a session.

    Returns:
        Response: HTTP response redirecting on success or rendering the login template.

    """
    try:
        if request.method == "OPTIONS":
            # Set CORS headers for the preflight (OPTIONS) request.
            response = await make_response("", 200)
            response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = request.headers.get(
                "Access-Control-Request-Headers", "Content-Type, Authorization"
            )
            return response

        db: SQLAlchemy = current_app.extensions["sqlalchemy"]
        request_json: dict[str, str] = await request.json

        if not request_json:
            return await make_response(jsonify({"message": "Erro ao efetuar login!"}), 400)

        username = request_json.get("login")
        password = request_json.get("password")
        remember = request_json.get("remember_me")
        form = LoginForm(username, password, remember)

        usr = db.session.query(Users).filter(Users.login == form.login).first()
        if usr and usr.check_password(form.password):
            access_token = create_access_token(identity=usr)
            refresh_token = create_refresh_token(identity=usr)

            # token = decode_token(access_token)
            isAdmin = True if usr.admin or usr.supersu else False  # noqa: N806

            resp = await make_response(
                jsonify({
                    "token": access_token,
                    "message": "Login efetuado com sucesso!",
                    "x-csrf-token": get_csrf_token(access_token),
                    "admin": isAdmin,
                })
            )

            # Set the JWT cookies in the response
            resp.status_code = 200
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)

            return resp

        resp = jsonify({"message": "Usuário ou senha incorretos!"})
        resp.status_code = 401
        resp.headers = {"Content-Type": "application/json"}
        return resp

    except Exception as e:
        rich.print(e)
        return await make_response(jsonify({"message": "Erro ao efetuar login!"}))


@auth.route("/logout", methods=["POST"])
async def logout() -> Response:
    """Log out the current user and clear session cookies.

    Returns:
        Response: Redirect response to the login page.

    """
    # db: SQLAlchemy = current_app.extensions["sqlalchemy"]
    # token = request.cookies.get("access_token_cookie")
    # if token:
    #     jti = token["jti"]
    #     ttype = token["type"]
    #     now = datetime.now(pytz.timezone("America/Manaus"))
    #     db.session.add(TokenBlocklist(jti=jti, type=ttype, created_at=now))
    #     db.session.commit()

    response = await make_response(jsonify(msg="Logout efetuado com sucesso!"))
    try:
        unset_jwt_cookies(response)

    except Exception as e:
        exc = "\n".join(format_exception(e))
        current_app.logger.exception("\n".join(exc))
    return response


# Rota para atualizar o token de acesso
@auth.route("/refresh", methods=["POST"])
@jwt_refresh_token_required
async def refresh() -> Response:
    """Refresh the access token."""
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return await make_response(jsonify(access_token=new_access_token), 200)
