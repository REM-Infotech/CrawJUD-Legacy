"""Module for bot operation routes."""

import os
import pathlib
import sys  # noqa: F401
import traceback

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
from quart_wtf import QuartForm

from web.decorators import login_required
from web.models import BotsCrawJUD

from ...forms import BotForm
from ...misc import MakeModels
from .botlaunch_methods import (
    get_bot_info,
    get_form_data,
    handle_form_errors,
    process_form_submission,
    process_form_submission_periodic,
    send_data_to_servers,
)

path_template = os.path.join(pathlib.Path(__file__).parent.resolve(), "templates")
bot = Blueprint("bot", __name__, template_folder=path_template)


@bot.route("/get_model/<id_>/<system>/<typebot>/<filename>", methods=["GET"])
async def get_model(id_: int, system: str, typebot: str, filename: str) -> Response:
    """Retrieve a model file for the specified bot.

    Args:
        id_ (int): Bot identifier.
        system (str): System being used.
        typebot (str): Type of bot.
        filename (str): Name of the file.

    Returns:
        Response: File download response.

    """
    try:
        with app.app_context():
            path_arquivo, nome_arquivo = MakeModels(filename, filename).make_output()
            response = await make_response(await send_file(f"{path_arquivo}", as_attachment=True))
            response.headers["Content-Disposition"] = f"attachment; filename={nome_arquivo}"
        return response

    except Exception as e:
        app.logger.exception(traceback.format_exc())
        abort(500, description=f"Erro interno. {e!s}")


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

        return await make_response(await render_template("index.html", page=page, bots=bots, title=title))

    except Exception as e:
        app.logger.exception(traceback.format_exc())
        abort(500, description=f"Erro interno. {e!s}")


@bot.route("/bot/<id_>/<system>/<typebot>", methods=["GET", "POST"])
@login_required
async def botlaunch(id_: int, system: str, typebot: str) -> Response:
    """Launch the specified bot process."""
    if not session.get("license_token"):
        await flash("Sessão expirada. Faça login novamente.", "error")
        return await make_response(redirect(url_for("auth.login")))

    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        bot_info = get_bot_info(db, id_)
        if not bot_info:
            await flash("Acesso negado!", "error")
            return await make_response(redirect(url_for("bot.dashboard")))

        display_name = bot_info.display_name
        title = display_name

        states, clients, credts, form_config = get_form_data(db, system, typebot, bot_info)

        form = await BotForm.create_form2(
            dynamic_fields=form_config,
            state=states,
            creds=credts,
            clients=clients,
            system=system,
        )
        if await QuartForm.validate_on_submit(form):
            periodic_bot = False
            data = {}
            if form.periodic_task.data is True:
                data, files, pid, periodic_bot = await process_form_submission_periodic(form, system, typebot, bot_info)

            elif form.periodic_task.data is False:
                data, files, pid = await process_form_submission(form, system, typebot, bot_info)

            response = await send_data_to_servers(
                data,
                files,
                {
                    "CONTENT_TYPE": request.content_type,
                },
                pid,
                periodic_bot,
            )
            if response:
                return response

        # for f in form.periodic_task_group:
        #     for pform in f:
        #         pass

        await handle_form_errors(form)

        url = request.base_url.replace("http://", "https://")
        return await make_response(
            await render_template(
                "index.html",
                page="botform.html",
                url=url,
                model_name=f"{system}_{typebot}",
                display_name=display_name,
                form=form,
                title=title,
                id=id_,
                system=system,
                typebot=typebot,
            )
        )

    except Exception:
        app.logger.exception(traceback.format_exc())
        abort(500, description="Erro interno.")
