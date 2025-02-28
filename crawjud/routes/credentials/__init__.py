"""Module for credentials routes.

This module defines endpoints for listing, creating, editing, and deleting credentials.
"""

import os
import pathlib
from collections import Counter

import aiofiles
from flask_sqlalchemy import SQLAlchemy
from quart import (
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
from quart import current_app as app
from werkzeug.utils import secure_filename

from crawjud.core import db
from crawjud.decorators import login_required
from crawjud.forms.credentials import CredentialsForm
from crawjud.models import BotsCrawJUD, Credentials, LicensesUsers

path_template = os.path.join(pathlib.Path(__file__).parent.resolve(), "templates")
cred = Blueprint("creds", __name__, template_folder=path_template)


@cred.route("/credentials/dashboard", methods=["GET"])
@login_required
async def credentials() -> Response:
    """Render the credentials dashboard page.

    Returns:
        Response: A Quart response rendering the credentials page.

    """
    if not session.get("license_token"):
        await flash("Sessão expirada. Faça login novamente.", "error")
        return await make_response(
            redirect(
                url_for(
                    "auth.login",
                ),
            ),
        )

    database = db.session.query(Credentials).join(LicensesUsers).filter_by(license_token=session["license_token"]).all()

    title = "Credenciais"
    page = "credentials.html"
    return await make_response(
        await render_template(
            "index.html",
            page=page,
            title=title,
            database=database,
        ),
    )


@cred.route("/credentials/cadastro", methods=["GET", "POST"])
@login_required
async def cadastro() -> Response:
    """Handle the creation of new credentials.

    Returns:
        Response: A Quart response after processing the credentials form.

    """
    if not session.get("license_token"):
        await flash("Sessão expirada. Faça login novamente.", "error")
        return await make_response(
            redirect(
                url_for(
                    "auth.login",
                ),
            ),
        )

    page = "FormCred.html"

    systems = [bot.system for bot in BotsCrawJUD.query.all()]
    count_system = Counter(systems).keys()

    system = [(syst, syst) for syst in count_system]

    form = await CredentialsForm.setup_form(system=system)

    func = "Cadastro"
    title = "Credenciais"

    action_url = url_for("creds.cadastro")

    if await form.validate_on_submit():
        if Credentials.query.filter(Credentials.nome_credencial == form.nome_cred.data).first():
            await flash("Existem credenciais com este nome já cadastrada!", "error")
            return await make_response(
                redirect(
                    url_for(
                        "creds.cadastro",
                    ),
                ),
            )

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

        async def cert(form: CredentialsForm) -> None:
            temporarypath = current_app.config["TEMP_DIR"]
            filecert = form.cert.data

            cer_path = os.path.join(temporarypath, secure_filename(filecert.filename))
            await filecert.save(cer_path)

            async with aiofiles.open(cer_path, "rb") as f:
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
                await func(form)
                break

        await flash("Credencial salva com sucesso!", "success")
        return await make_response(
            redirect(
                url_for(
                    "creds.credentials",
                ),
            ),
        )

    return await make_response(
        await render_template(
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
async def editar(id_: int = None) -> Response:
    """Handle editing an existing credential.

    Args:
        id_ (int, optional): The credential identifier.

    Returns:
        Response: A Quart response rendering the edit form.

    """
    page = "FormCred.html"

    systems = [bot.system for bot in BotsCrawJUD.query.all()]
    count_system = Counter(systems).keys()

    system = [(syst, syst) for syst in count_system]

    form = await CredentialsForm.setup_form(system=system)

    func = "Cadastro"
    title = "Credenciais"

    action_url = url_for("creds.cadastro")

    if await form.validate_on_submit():
        await flash("Credencial salva com sucesso!", "success")
        return await make_response(
            redirect(
                url_for(
                    "creds.credentials",
                ),
            ),
        )

    return await make_response(
        await render_template(
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
async def deletar(id_: int = None) -> Response:
    """Delete a credential identified by its id.

    Args:
        id_ (int, optional): The credential identifier.

    Returns:
        Response: A Quart response confirming deletion.

    """
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    to_delete = db.session.query(Credentials).filter(Credentials.id == id_).first()

    db.session.delete(to_delete)
    db.session.commit()

    message = "Credencial deletada!"

    template = "include/show.html"
    return await make_response(
        await render_template(
            template,
            message=message,
        ),
    )
