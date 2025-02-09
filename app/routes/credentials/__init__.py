"""Module for credentials routes.

This module defines endpoints for listing, creating, editing, and deleting credentials.
"""

import os
from collections import Counter
from pathlib import Path

from flask_login import login_required
from quart import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from app import db
from app.forms.credentials import CredentialsForm
from app.models import BotsCrawJUD, Credentials, LicensesUsers

path_template = Path(__file__).parent.resolve().joinpath("templates")
cred = Blueprint("creds", __name__, template_folder=path_template)


@cred.route("/credentials/dashboard", methods=["GET"])
@login_required
async def credentials():
    """Render the credentials dashboard page.

    Returns:
        Response: A Quart response rendering the credentials page.

    """
    if not session.get("license_token"):
        flash("Sessão expirada. Faça login novamente.", "error")
        return redirect(url_for("auth.login"))

    database = db.session.query(Credentials).join(LicensesUsers).filter_by(license_token=session["license_token"]).all()

    title = "Credenciais"
    page = "credentials.html"
    return await render_template("index.html", page=page, title=title, database=database)


@cred.route("/credentials/cadastro", methods=["GET", "POST"])
@login_required
async def cadastro():
    """Handle the creation of new credentials.

    Returns:
        Response: A Quart response after processing the credentials form.

    """
    if not session.get("license_token"):
        flash("Sessão expirada. Faça login novamente.", "error")
        return redirect(url_for("auth.login"))

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
            return redirect(url_for("creds.cadastro"))

        async def pw(form) -> None:
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

        async def cert(form) -> None:
            temporarypath = current_app.config["TEMP_PATH"]
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
        return redirect(url_for("creds.credentials"))

    return await render_template(
        "index.html",
        page=page,
        form=form,
        title=title,
        func=func,
        action_url=action_url,
    )


@cred.route("/credentials/editar/<id>", methods=["GET", "POST"])
@login_required
async def editar(id: int = None):
    """Handle editing an existing credential.

    Args:
        id (int, optional): The credential identifier.

    Returns:
        Response: A Quart response rendering the edit form.

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
        return redirect(url_for("creds.credentials"))

    return await render_template(
        "index.html",
        page=page,
        form=form,
        title=title,
        func=func,
        action_url=action_url,
    )


@cred.route("/credentials/deletar/<id>", methods=["GET", "POST"])
@login_required
async def deletar(id: int = None):
    """Delete a credential identified by its id.

    Args:
        id (int, optional): The credential identifier.

    Returns:
        Response: A Quart response confirming deletion.

    """
    to_delete = Credentials.query.filter(Credentials.id == id).first()

    db.session.delete(to_delete)
    db.session.commit()

    message = "Credencial deletada!"

    template = "include/show.html"
    return await render_template(template, message=message)
