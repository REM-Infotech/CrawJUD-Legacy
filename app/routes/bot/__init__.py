"""Module for bot operation routes."""

import os
import pathlib
import traceback

from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from quart import (
    Blueprint,
    Response,
    abort,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from quart import current_app as app

from app.models import BotsCrawJUD

from ...forms import BotForm
from ...misc import MakeModels
from .botlaunch_methods import (
    get_bot_info,
    get_form_data,
    handle_form_errors,
    process_form_submission,
    send_data_to_servers,
)

path_template = os.path.join(pathlib.Path(__file__).parent.resolve(), "templates")
bot = Blueprint("bot", __name__, template_folder=path_template)


@bot.route("/get_model/<id>/<system>/<typebot>/<filename>", methods=["GET"])
async def get_model(id: int, system: str, typebot: str, filename: str) -> Response:  # noqa: A002
    """Retrieve a model file for the specified bot.

    Args:
        id (int): Bot identifier.
        system (str): System being used.
        typebot (str): Type of bot.
        filename (str): Name of the file.

    Returns:
        Response: File download response.

    """
    try:
        path_arquivo, nome_arquivo = MakeModels(filename, filename).make_output()
        response = make_response(send_file(f"{path_arquivo}", as_attachment=True))
        response.headers["Content-Disposition"] = f"attachment; filename={nome_arquivo}"
        return response

    except Exception as e:
        app.logger.exception(traceback.format_exc())
        abort(500, description=f"Erro interno. {str(e)}")


@bot.route("/bot/dashboard", methods=["GET"])
@login_required
async def dashboard() -> Response:
    """Render the bot dashboard page.

    Returns:
        Response: HTTP response with rendered template.

    """
    try:
        title = "Robôs"
        page = "botboard.html"
        bots = BotsCrawJUD.query.all()

        return make_response(render_template("index.html", page=page, bots=bots, title=title))

    except Exception as e:
        app.logger.exception(traceback.format_exc())
        abort(500, description=f"Erro interno. {str(e)}")


@bot.route("/bot/<id>/<system>/<typebot>", methods=["GET", "POST"])
@login_required
async def botlaunch(id: int, system: str, typebot: str) -> Response:  # noqa: A002
    """Launch the specified bot process."""
    if not session.get("license_token"):
        flash("Sessão expirada. Faça login novamente.", "error")
        return make_response(redirect(url_for("auth.login")))

    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        bot_info = get_bot_info(db, id)
        if not bot_info:
            flash("Acesso negado!", "error")
            return make_response(redirect(url_for("bot.dashboard")))

        display_name = bot_info.display_name
        title = display_name

        states, clients, credts, form_config = get_form_data(db, system, typebot, bot_info)

        form = BotForm(
            dynamic_fields=form_config,
            state=states,
            creds=credts,
            clients=clients,
            system=system,
        )

        if form.validate_on_submit():
            data, files, pid = process_form_submission(form, system, typebot, bot_info)
            response = send_data_to_servers(data, files, {"CONTENT_TYPE": request.environ["CONTENT_TYPE"]}, pid)
            if response:
                return response

        handle_form_errors(form)

        url = request.base_url.replace("http://", "https://")
        return make_response(
            render_template(
                "index.html",
                page="botform.html",
                url=url,
                model_name=f"{system}_{typebot}",
                display_name=display_name,
                form=form,
                title=title,
                id=id,
                system=system,
                typebot=typebot,
            )
        )

    except Exception:
        app.logger.exception(traceback.format_exc())
        abort(500, description="Erro interno.")
