"""Module for execution routes.

This module provides endpoints for listing executions and downloading execution files.
"""

import os
import pathlib
from importlib import import_module
from traceback import format_exception

from flask_sqlalchemy import SQLAlchemy
from quart import (
    Blueprint,
    Response,
    abort,
    jsonify,
    make_response,
    render_template,
)
from quart import current_app as app
from quart_jwt_extended import (  # noqa: F401
    create_access_token,
    get_jwt_identity,
    jwt_refresh_token_required,
    jwt_required,
)

from api import db
from api.models import Executions, Users
from api.models import SuperUser as SuperUser
from api.models import admins as admins

# from crawjud.forms import SearchExec as SearchExec
from crawjud.misc import generate_signed_url

path_template = os.path.join(pathlib.Path(__file__).parent.resolve(), "templates")
exe = Blueprint("exe", __name__, template_folder=path_template)


@exe.route("/executions", methods=["GET", "POST"])
@jwt_required
async def executions() -> Response:
    """Display a list of executions filtered by search criteria.

    Returns:
        Response: A Quart response rendering the executions page.

    """
    try:
        data = []

        current_user = get_jwt_identity()

        executions = db.session.query(Executions).all()
        user = db.session.query(Users).filter(Users.id == current_user).first()

        if not user.supersu:
            executions = list(
                filter(lambda x: str(x.license_usr.license_token) == str(user.licenseusr.license_token), executions)
            )

            if not user.admin:
                executions = list(filter(lambda x: x.user.id == current_user, executions))

        for item in executions:
            data.append({
                "pid": item.pid,
                "user": item.user.nome_usuario,
                "botname": item.bot.display_name,
                "xlsx": item.arquivo_xlsx,
                "start_date": item.data_execucao,
                "status": item.status,
                "stop_date": item.data_finalizacao,
                "file_output": item.file_output,
            })

        return jsonify(data=data)

    except Exception as e:
        app.logger.error("\n".join(format_exception(e)))
        abort(500)


@exe.route("/executions/download/<filename>")
@jwt_required
async def download_file(filename: str) -> Response:
    """Generate a signed URL and redirect to the file download.

    Args:
        filename (str): The name of the file to download.

    Returns:
        Response: A Quart redirect response to the signed URL.

    """
    signed_url = generate_signed_url(filename)

    # Redireciona para a URL assinada
    return await make_response(jsonify(url=signed_url))


def schedule_route() -> None:
    """Import the schedules module and add the route to the Quart application."""
    import_module(".schedules", __package__)


schedule_route()


@exe.post("/clear_executions")
@jwt_required
async def clear_executions() -> Response:
    """Clear all executions from the database."""
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        db.session.query(Executions).filter(Executions.status == "Finalizado").delete()
        db.session.commit()

    except Exception as e:
        app.logger.exception(str(e))
        abort(500)

    message = "Execuções removidas com sucesso!"
    template = "include/show.html"
    return await make_response(
        await render_template(
            template,
            message=message,
        ),
    )
