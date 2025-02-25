"""Module for authentication routes."""

import json
import os
import pathlib


from flask_login import login_user, logout_user
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

from web.forms import LoginForm
from web.models.users import Users

path_template = os.path.join(pathlib.Path(__file__).parent.resolve(), "templates")
auth = Blueprint("auth", __name__, template_folder=path_template)

usr = None


@auth.before_request
def nexturl() -> None:
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

    if form.validate_on_submit():
        usr = Users.query.filter(Users.login == form.login.data).first()
        if usr is None or not usr.check_password(form.password.data):
            await flash("Senha incorreta!", "error")
            return await make_response(redirect(url_for("auth.login")))

        if not session.get("location"):
            session["location"] = url_for("dash.dashboard")

        login_user(usr, remember=form.remember_me.data)
        resp = await make_response(redirect(session["location"]))

        if usr.admin:
            is_admin = json.dumps({"login_id": session["_id"]})
            resp.set_cookie(
                "roles_admin",
                is_admin,
                max_age=60 * 60 * 24,
                httponly=True,
                secure=True,
                samesite="Lax",
            )

        if usr.supersu:
            is_supersu = json.dumps({"login_id": session["_id"]})
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
# def forgot_password():
#     """Handle the forgot password functionality.

#     Returns:
#         str: Currently an empty string.

#     """
#     return await make_response()


@auth.route("/logout", methods=["GET", "POST"])
async def logout() -> Response:
    """Log out the current user and clear session cookies.

    Returns:
        Response: Redirect response to the login page.

    """
    logout_user()

    await flash("Logout efetuado com sucesso!", "success")
    resp = redirect(url_for("auth.login"))

    cookies_ = list(request.cookies.keys())
    for cookie in cookies_:
        if cookie != "session":
            resp.set_cookie(cookie, "", max_age=0)

    iter_session = list(session.keys())
    for key in iter_session:
        if "_" not in key:
            session.pop(key)

    return await make_response(resp)
