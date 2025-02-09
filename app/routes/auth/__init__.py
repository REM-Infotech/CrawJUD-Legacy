"""Module for authentication routes."""

import hashlib
import json
from pathlib import Path

from flask_sqlalchemy import SQLAlchemy
from quart import (
    Blueprint,
    Response,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from quart import (
    current_app as app,
)
from quart_auth import AuthUser, login_user, logout_user

from app.forms.auth.login import LoginForm
from app.models.users import Users

path_template = Path(__file__).parent.resolve().joinpath("templates")
auth = Blueprint("auth", __name__, template_folder=path_template)

usr = None


@auth.before_request
async def nexturl() -> None:
    """Store the next URL in session if provided.

    Returns:
        None

    """
    if request.args.get("next"):
        session["location"] = request.args.get("next")


@auth.route("/login", methods=["GET", "POST"])
async def login() -> Response:
    """Authenticate the user and start a session.

    Returns:
        Response: HTTP response redirecting on success or rendering the login template.

    """
    form = LoginForm()
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    if form.validate_on_submit():
        usr = db.session.query(Users).filter(Users.login == form.login.data).first()
        if usr is None or not usr.check_password(form.password.data):
            await flash("Senha incorreta!", "error")
            return await make_response(redirect(url_for("auth.login")))

        if not session.get("location"):
            session["location"] = url_for("dash.dashboard")

        to_login = {}
        usr_dict = usr.__dict__
        for key, value in list(usr_dict.items()):
            if "_" not in key:
                to_login[key] = value

        usr_auth = AuthUser(to_login)

        session["_id"] = hashlib.sha512(str(usr_auth.auth_id).encode()).hexdigest()

        login_user(usr_auth, remember=form.remember_me.data)
        resp = await make_response(redirect(session["location"]))

        if usr.admin:
            is_admin = json.dumps({"login_id": session.get("_id")})
            resp.set_cookie(
                "roles_admin",
                is_admin,
                max_age=60 * 60 * 24,
                httponly=True,
                secure=True,
                samesite="Lax",
            )

        if usr.supersu:
            is_supersu = json.dumps({"login_id": session.get("_id")})
            resp.set_cookie(
                "roles_supersu",
                is_supersu,
                max_age=60 * 60 * 24,
                httponly=True,
                secure=True,
                samesite="Lax",
            )

        license_usr = usr.licenseusr
        session.permanent = form.remember_me.data
        session["login"] = usr.login
        session["nome_usuario"] = usr.nome_usuario
        session["license_token"] = license_usr.license_token

        await flash("Login efetuado com sucesso!", "success")
        return resp

    return await make_response(await render_template("login.html", form=form))


# @auth.route("/forgot-password", methods=["GET", "POST"])
# async def forgot_password():
#     """Handle the forgot password functionality.

#     Returns:
#         str: Currently an empty string.

#     """
#     return


@auth.route("/logout", methods=["GET", "POST"])
async def logout() -> Response:
    """Log out the current user and clear session cookies.

    Returns:
        Response: Redirect response to the login page.

    """
    logout_user()

    await flash("Logout efetuado com sucesso!", "success")
    resp = make_response(redirect(url_for("auth.login")))

    cookies_ = list(request.cookies.keys())
    for cookie in cookies_:
        if cookie != "session":
            resp.set_cookie(cookie, "", max_age=0)

    iter_session = list(session.keys())
    for key in iter_session:
        if "_" not in key:
            session.pop(key)

    return await resp
