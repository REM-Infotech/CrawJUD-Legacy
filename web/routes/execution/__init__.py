"""Module for execution routes.

This module provides endpoints for listing executions and downloading execution files.
"""

import os
import pathlib
from importlib import import_module

from flask_sqlalchemy import SQLAlchemy
from quart import (
    Blueprint,
    Response,
    abort,
    make_response,
    redirect,
    render_template,
    request,
    session,
)
from quart import current_app as app
from sqlalchemy.orm import aliased

from web import db
from web.decorators import login_required
from web.forms import SearchExec
from web.misc import generate_signed_url
from web.models import Executions, SuperUser, Users, admins

path_template = os.path.join(pathlib.Path(__file__).parent.resolve(), "templates")
exe = Blueprint("exe", __name__, template_folder=path_template)


@exe.route("/executions", methods=["GET", "POST"])
@login_required
async def executions() -> Response:
    """Display a list of executions filtered by search criteria.

    Returns:
        Response: A Quart response rendering the executions page.

    """
    try:
        form = SearchExec()
        pid = request.args.get("pid", "")

        if form.validate_on_submit():
            pid = form.campo_busca.data

        chksupersu = (
            db.session.query(SuperUser)
            .select_from(Users)
            .join(Users.supersu)
            .filter(Users.login == session["login"])
            .first()
        )

        executions = db.session.query(Executions)

        if chksupersu:
            alias = aliased(
                Users,
                (db.session.query(Users).filter(Users.login == session["login"]).subquery()),
            )

            executions = executions.join(alias, Executions.license_id == alias.licenseus_id)

            chk_admin = (
                db.session.query(admins)
                .join(alias, admins.c.users_id == alias.id)
                .filter(admins.c.license_user_id == alias.licenseus_id)
                .first()
            )

            if not chk_admin:
                executions = executions.join(Users, Executions.user).filter(Users.login == session["login"])

        executions = executions.filter(Executions.pid.contains(pid))
        database = executions.all()

    except Exception:
        abort(500)

    title = "Execuções"
    page = "executions.html"
    return await make_response(
        await render_template(
            "index.html",
            page=page,
            title=title,
            database=database,
            form=form,
        )
    )


@exe.route("/executions/download/<filename>")
@login_required
async def download_file(filename: str) -> Response:
    """Generate a signed URL and redirect to the file download.

    Args:
        filename (str): The name of the file to download.

    Returns:
        Response: A Quart redirect response to the signed URL.

    """
    signed_url = generate_signed_url(filename)

    # Redireciona para a URL assinada
    return await make_response(
        redirect(
            signed_url,
        ),
    )


def schedule_route() -> None:
    """Import the schedules module and add the route to the Quart application."""
    import_module(".schedules", __package__)


schedule_route()


@exe.post("/clear_executions")
@login_required
async def clear_executions() -> Response:
    """Clear all executions from the database."""
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        db.session.query(Executions).filter(Executions.status == "Finalizado").delete()
        db.session.commit()

    except Exception as e:
        app.logger.error(str(e))
        abort(500)

    message = "Execuções removidas com sucesso!"
    template = "include/show.html"
    return await make_response(
        await render_template(
            template,
            message=message,
        ),
    )
