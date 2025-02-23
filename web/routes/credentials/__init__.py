"""Module for credentials routes.

This module defines endpoints for listing, creating, editing, and deleting credentials.
"""

import os
import pathlib
from collections import Counter

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    make_response,
    redirect,
    render_template,
    session,
    url_for,
)
from flask import current_app as app
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

from web import db
from web.forms.credentials import CredentialsForm
from web.models import BotsCrawJUD, Credentials, LicensesUsers

path_template = os.path.join(pathlib.Path(__file__).parent.resolve(), "templates")
cred = Blueprint("creds", __name__, template_folder=path_template)


@cred.route("/credentials/dashboard", methods=["GET"])
@login_required
def credentials() -> Response:
    """Render the credentials dashboard page.

    Returns:
        Response: A Flask response rendering the credentials page.

    """
    if not session.get("license_token"):
        flash("Sessão expirada. Faça login novamente.", "error")
        return make_response(redirect(url_for("auth.login")))

    database = db.session.query(Credentials).join(LicensesUsers).filter_by(license_token=session["license_token"]).all()

    title = "Credenciais"
    page = "credentials.html"
    return make_response(render_template("index.html", page=page, title=title, database=database))


@cred.route("/credentials/cadastro", methods=["GET", "POST"])
@login_required
def cadastro() -> Response:
    """Handle the creation of new credentials.

    Returns:
        Response: A Flask response after processing the credentials form.

    """
    if not session.get("license_token"):
        flash("Sessão expirada. Faça login novamente.", "error")
        return make_response(redirect(url_for("auth.login")))

    page = "FormCred.html"

    systems = [bot.system for bot in BotsCrawJUD.query.all()]
    count_system = Counter(systems).keys()

    system = [(syst, syst) for syst in count_system]

    form = CredentialsForm(system=system)

    func = "Cadastro"
    title = "Credenciais"

    action_url = url_for("creds.cadastro")

    if form.validate_on_submit():
        if Credentials.query.filter(Credentials.nome_credencial == form.nome_cred.data).first():
            flash("Existem credenciais com este nome já cadastrada!", "error")
            return make_response(redirect(url_for("creds.cadastro")))

        def pw(form: CredentialsForm) -> None:
            passwd = Credentials(
                nome_credencial=form.nome_cred.data,
                system=form.system.data,
                login_method=form.auth_method.data,
                login=form.login.data,
                password=form.password.data,
            )
            licenseusr = LicensesUsers.query.filter(LicensesUsers.license_token == session["license_token"]).first()

            passwd.license_usr = licenseusr
            db.session.add(passwd)
            db.session.commit()

        def cert(form: CredentialsForm) -> None:
            temporarypath = current_app.config["TEMP_DIR"]
            filecert = form.cert.data

            cer_path = os.path.join(temporarypath, secure_filename(filecert.filename))
            filecert.save(cer_path)

            with open(cer_path, "rb") as f:
                certficate_blob = f.read()

            passwd = Credentials(
                nome_credencial=form.nome_cred.data,
                system=form.system.data,
                login_method=form.auth_method.data,
                login=form.doc_cert.data,
                key=form.key.data,
                certficate=filecert.filename,
                certficate_blob=certficate_blob,
            )
            licenseusr = LicensesUsers.query.filter(LicensesUsers.license_token == session["license_token"]).first()

            passwd.license_usr = licenseusr

            db.session.add(passwd)
            db.session.commit()

        local_defs = list(locals().items())
        for name, func in local_defs:
            if name == form.auth_method.data:
                func(form)
                break

        flash("Credencial salva com sucesso!", "success")
        return make_response(redirect(url_for("creds.credentials")))

    return make_response(
        render_template(
            "index.html",
            page=page,
            form=form,
            title=title,
            func=func,
            action_url=action_url,
        )
    )


@cred.route("/credentials/editar/<id_>", methods=["GET", "POST"])
@login_required
def editar(id_: int = None) -> Response:
    """Handle editing an existing credential.

    Args:
        id_ (int, optional): The credential identifier.

    Returns:
        Response: A Flask response rendering the edit form.

    """
    page = "FormCred.html"

    systems = [bot.system for bot in BotsCrawJUD.query.all()]
    count_system = Counter(systems).keys()

    system = [(syst, syst) for syst in count_system]

    form = CredentialsForm(system=system)

    func = "Cadastro"
    title = "Credenciais"

    action_url = url_for("creds.cadastro")

    if form.validate_on_submit():
        flash("Credencial salva com sucesso!", "success")
        return make_response(redirect(url_for("creds.credentials")))

    return make_response(
        render_template(
            "index.html",
            page=page,
            form=form,
            title=title,
            func=func,
            action_url=action_url,
        )
    )


@cred.route("/credentials/deletar/<id_>", methods=["GET", "POST"])
@login_required
def deletar(id_: int = None) -> Response:
    """Delete a credential identified by its id.

    Args:
        id_ (int, optional): The credential identifier.

    Returns:
        Response: A Flask response confirming deletion.

    """
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    to_delete = db.session.query(Credentials).filter(Credentials.id == id_).first()

    db.session.delete(to_delete)
    db.session.commit()

    message = "Credencial deletada!"

    template = "include/show.html"
    return make_response(render_template(template, message=message))
