"""Module for Admin configuration routes."""

from pathlib import Path
from typing import Dict

from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from quart import Blueprint, Response, abort, flash, make_response, redirect, render_template, session, url_for
from quart import current_app as app

from app.forms import UserForm, UserFormEdit
from app.models import LicensesUsers, SuperUser, Users

path_template = Path(__file__).parent.resolve().joinpath("templates")
admin = Blueprint("admin", __name__, template_folder=path_template)


@admin.route("/users", methods=["GET"])
@login_required
async def users() -> Response:
    """Render the users list template.

    Returns:
        Response: HTTP response with rendered template.

    """
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]

        user = db.session.query(Users).filter(Users.login == session["login"]).first()
        user_id = user.id

        chksupersu = db.session.query(SuperUser).join(Users).filter(Users.id == user_id).first()

        users = db.session.query(Users)
        if not chksupersu:
            users = users.join(LicensesUsers).filter_by(license_token=user.licenseusr.license_token)

        database = users.all()

        page = "users.html"
        return make_response(render_template("index.html", page=page, database=database))

    except Exception as e:
        abort(500, description=f"Erro interno do servidor: {str(e)}")


@admin.route("/cadastro/usuario", methods=["GET", "POST"])
@login_required
async def cadastro_user() -> Response:
    """Handle user registration.

    Returns:
        Response: HTTP response redirecting or rendering the template.

    """
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        if not session.get("license_token"):
            flash("Sessão expirada. Faça login novamente.", "error")
            return redirect(url_for("auth.login"))

        title = "Cadastro Usuário"
        form = UserForm()
        page = "FormUsr.html"

        user = Users.query.filter(Users.login == session["login"]).first()
        user_id = user.id

        chksupersu = db.session.query(SuperUser).join(Users).filter(Users.id == user_id).first()

        if chksupersu:
            licenses = []
            licenses_result = LicensesUsers.query.all()

            for lcs in licenses_result:
                licenses.append((str(lcs.license_token), str(lcs.name_client)))

            form = UserForm(licenses_add=licenses_result)

        if form.validate_on_submit():
            user = Users(
                login=form.login.data,
                nome_usuario=form.nome_usuario.data,
                email=form.email.data,
            )

            license_token = session["license_token"]
            tipo_user = form.tipo_user.data

            if chksupersu:
                if any(tipo_user == tipo for tipo in ["default_user", "admin"]):
                    license_token = form.licenses.data

                elif tipo_user == "supersu":
                    super_user = SuperUser()
                    super_user.users = user

            query_license = LicensesUsers.query.filter(LicensesUsers.license_token == license_token).first()

            user.licenseusr = query_license

            if tipo_user == "admin":
                query_license.admins.append(user)

            user.senhacrip = form.password.data

            db.session.add(user)
            db.session.commit()

            flash("Usuário cadastrado!", "success")
            return redirect(url_for("admin.users"))

        form_items = list(form)
        for field in form_items:
            for error in field.errors:
                flash(f"Erro: {error}. Campo: {field.label.text}", "error")

        return make_response(render_template("index.html", page=page, form=form, title=title))

    except Exception as e:
        abort(500, description=f"Erro interno do servidor: {str(e)}")


@admin.route("/editar/usuario/<id>", methods=["GET", "POST"])
@login_required
async def edit_usuario(id: int) -> Response:
    """Handle editing a user with the given id.

    Args:
        id (int): The user's id.

    Returns:
        Response: HTTP response redirecting or rendering the template.

    """
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        if not session.get("license_token"):
            flash("Sessão expirada. Faça login novamente.", "error")
            return redirect(url_for("auth.login"))

        title = "Editar Usuário"

        user = db.session.query(Users).filter(Users.id == id).first()

        form = UserFormEdit(**user.dict_query)
        page = "FormUsr.html"

        chksupersu = db.session.query(SuperUser).join(Users).filter(Users.login == session["login"]).first()

        if chksupersu:
            licenses_result = db.session.query(LicensesUsers).all()

            form = UserFormEdit(
                licenses_add=licenses_result,
                **user.dict_query,
            )

        if form.validate_on_submit():
            data: Dict[str, str | bool] = form.data

            [
                setattr(user, key, value)
                for key, value in {
                    key: value
                    for key, value in data.items()
                    if key
                    not in [
                        "show_password",
                        "csrf_token",
                        "submit",
                        "password",
                        "tipo_user",
                        "license",
                    ]
                }.items()
            ]

            license_token = data.get("licenses", session["license_token"])
            license_user = db.session.query(LicensesUsers).filter(LicensesUsers.license_token == license_token).first()

            password = data.get("password")

            if user.login != session["login"]:
                if chksupersu:
                    if data.get("tipo_user") == "supersu" and len(user.supersu) == 0:
                        if chksupersu:
                            super_user = SuperUser()
                            super_user.users = user

                            db.session.add(super_user)

                    elif data.get("tipo_user") != "supersu" and len(user.supersu) > 0:
                        supersu = db.session.query(SuperUser).filter(SuperUser.users_id == user.id).first()

                        db.session.delete(supersu)

                if data.get("tipo_user") == "admin" and len(user.admin) == 0:
                    license_user.admins.append(user)

                elif data.get("tipo_user") != "admin" and len(user.admin) > 0:
                    license_user.admins.remove(user)

            if password:
                if user.check_password(password) is not True:
                    user.senhacrip = password

            db.session.commit()

            flash("Usuário editado com sucesso!", "message")
            return make_response(redirect(url_for("admin.users")))

        return make_response(render_template("index.html", page=page, form=form, title=title))

    except Exception as e:
        abort(500, description=f"Erro interno do servidor: {str(e)}")


@admin.route("/deletar/usuario/<id>", methods=["GET", "POST"])
@login_required
async def delete_usuario(id: int) -> Response:
    """Handle deletion of a user with the given id.

    Args:
        id (int): The user's id.

    Returns:
        Response: HTTP response with the delete confirmation.

    """
    try:
        title = "Editar Usuário"
        form = UserForm()
        page = "FormUsr.html"

        flash("Hello World!", "success")
        return make_response(render_template("index.html", page=page, form=form, title=title))

    except Exception as e:
        abort(500, description=f"Erro interno do servidor: {str(e)}")
