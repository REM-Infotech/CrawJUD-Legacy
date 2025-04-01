"""Module for bot operation routes."""

import json  # noqa: F401
import os
import sys  # noqa: F401
import warnings
from pathlib import Path
from traceback import format_exception

from flask_sqlalchemy import SQLAlchemy
from quart import (
    Blueprint,
    Response,
    abort,
    jsonify,
    make_response,
    render_template,
    request,
    send_file,
)
from quart import current_app as app
from quart_jwt_extended import get_jwt_identity, jwt_required
from quart_wtf import QuartForm  # noqa: F401

from api.models import BotsCrawJUD
from api.models.bots import Credentials
from api.models.users import LicensesUsers

# from crawjud.forms import BotForm as BotForm
from crawjud.misc import MakeModels
from crawjud.utils.gen_seed import generate_pid

from .botlaunch_methods import (
    get_bot_info,
    license_user,
    setup_task_worker,  # noqa: F401
)
from .botlaunch_methods import get_form_data as get_form_data

path_template = os.path.join(Path(__file__).parent.resolve(), "templates")
bot = Blueprint("bot", __name__, template_folder=path_template)


@bot.route("/acquire_credentials", methods=["post"])
@jwt_required
async def acquire_credentials() -> Response:
    """Return a list credentials."""
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        json_data: dict[str, str] = await request.json
        form_data = request.form

        if not json_data:
            json_data = await form_data

        system = json_data["system"]

        form_cfg = json_data["form_cfg"]

        if form_cfg == "only_file":
            return jsonify({"value": "Opção não utilizada", "text": "Opção não utilizada", "disabled": True})

        cred = [{"value": None, "text": "Selecione uma credencial", "disabled": True}]

        license_token = await license_user(get_jwt_identity(), app.extensions["sqlalchemy"])

        creds = (
            db.session.query(Credentials)
            .select_from(LicensesUsers)
            .join(LicensesUsers, Credentials.license_usr)
            .filter(LicensesUsers.license_token == license_token)
            .all()
        )
        cred.extend([
            {"value": credential.nome_credencial, "text": credential.nome_credencial}
            for credential in creds
            if credential.system == system.upper()
        ])
        return jsonify(info=cred)

    except Exception as e:
        app.logger.error("\n".join(format_exception(e)))
        return jsonify({}, 500)


@bot.route("/acquire_systemclient", methods=["post"])
@jwt_required
async def acquire_systemclient() -> Response:
    """Return a list credentials."""
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        json_data: dict[str, str] = await request.json
        form_data = request.form

        if not json_data:
            json_data = await form_data

        system = json_data["system"]
        typebot = json_data["type"]

        client = json_data["client"]
        state = json_data["state"]

        # usr = get_jwt_identity()
        form_cfg = json_data["form_cfg"]

        if form_cfg == "only_file":
            return jsonify({"value": "Opção não utilizada", "text": "Opção não utilizada", "disabled": True})

        if state == "EVERYONE":
            type_ = "client"
            opt = [{"value": None, "text": "Selecione um cliente", "disabled": True}]

            opt.extend([
                {"value": client.client, "text": client.client}
                for client in db.session.query(BotsCrawJUD)
                .filter(
                    BotsCrawJUD.type == typebot.upper(),
                    BotsCrawJUD.system == system.upper(),
                )
                .all()
            ])
            return jsonify(info=opt, type=type_)

        elif client == "EVERYONE":
            opt = [{"value": None, "text": "Selecione um Estado", "disabled": True}]
            type_ = "state"
            opt.extend([
                {"value": state.state, "text": state.state}
                for state in db.session.query(BotsCrawJUD)
                .filter(
                    BotsCrawJUD.type == typebot.upper(),
                    BotsCrawJUD.system == system.upper(),
                )
                .all()
            ])
            return jsonify(info=opt, type=type_)

    except Exception as e:
        app.logger.error("\n".join(format_exception(e)))
        return jsonify({}, 500)


@bot.route("/bots_list", methods=["get"])
@jwt_required
async def bots_list() -> Response:
    """Return a list bots."""
    try:
        bots_ = []

        db: SQLAlchemy = app.extensions["sqlalchemy"]
        # path_current_file = Path(__file__).parent.resolve()
        # path_json = path_current_file.joinpath("bots.json")
        # # with path_json.open("r", encoding="utf-8") as f:
        # #     # bots_ = json.loads(f.read())

        # # return jsonify(bots_)

        bots = db.session.query(BotsCrawJUD).all()

        for bot in bots:
            bots_.append({
                "id": bot.id,
                "display_name": bot.display_name,
                "system": bot.system.upper(),
                "state": bot.state.upper(),
                "client": bot.client.upper(),
                "type": bot.type.upper(),
                "form_cfg": bot.form_cfg.lower(),
                "classification": bot.classification.upper(),
                "text": bot.text,
            })

        return jsonify(bots_)

    except Exception as e:
        app.logger.error("\n".join(format_exception(e)))


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
        async with app.app_context():
            path_arquivo, nome_arquivo = MakeModels(filename, filename).make_output()
            response = await make_response(await send_file(f"{path_arquivo}", as_attachment=True))
            response.headers["Content-Disposition"] = f"attachment; filename={nome_arquivo}"
        return response

    except Exception as e:
        app.logger.exception("\n".join(format_exception(e)))
        abort(500, description=f"Erro interno. {e!s}")


@bot.route("/bot/dashboard", methods=["GET"])
@jwt_required
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
        app.logger.exception("\n".join(format_exception(e)))
        abort(500, description=f"Erro interno. {e!s}")


@bot.route("/bot/<id_>/<system>/<typebot>", methods=["POST"])
@jwt_required
async def botlaunch(id_: int, system: str, typebot: str) -> Response:
    """Launch the specified bot process."""
    form = {}
    data = await request.form
    files = await request.files  # noqa: F841
    pid = generate_pid()
    try:
        form.update(data)
        form.update(files)

        periodic_bot = False

        db: SQLAlchemy = app.extensions["sqlalchemy"]
        bot_info = await get_bot_info(db, id_)
        if not bot_info:
            return await make_response(jsonify(response="Erro ao iniciar"), 500)

        display_name = bot_info.display_name
        title = display_name  # noqa: F841

        if not form:
            return await make_response(jsonify(response="ok"), 403)  # noqa: F841

        return await setup_task_worker(  # noqa: B012
            id_=id_,
            pid=pid,
            form=form,
            system=system,
            typebot=typebot,
            periodic_bot=periodic_bot,
            bot_info=bot_info,
        )

    except Exception as e:
        app.logger.exception("\n".join(format_exception(e)))
        abort(500, description="Erro interno.")

    finally:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)

        except Exception as e:
            app.logger.exception("\n".join(format_exception(e)))
            # abort(500, description="Erro interno.")
