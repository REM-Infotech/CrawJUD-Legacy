"""Module for Admin configuration routes."""

from __future__ import annotations

import json
from traceback import format_exception
from typing import TYPE_CHECKING, Literal
from zoneinfo import ZoneInfo

from quart import (
    Response,
    abort,
    jsonify,
    make_response,
    request,
    session,
)
from quart import current_app as app
from quart_jwt_extended import get_jwt_identity, jwt_required

from crawjud.common.exceptions.database import (
    DeleteError,
    InsertError,
    UpdateError,
)
from crawjud.interfaces.dict import ActionsDict
from crawjud.interfaces.session import SessionDict
from crawjud.models import LicensesUsers, Users
from crawjud.models import SuperUser as SuperUser

from . import admin

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy

    from crawjud.interfaces.types import DictType
    from crawjud.interfaces.types.literals import (
        CallableMethodRequest,
        MethodRequested,
    )


def license_(usr: int) -> LicensesUsers | None:
    """Get the user's license.

    Returns:
        LicensesUsers | None: License of the user or None if not found.

    """
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    return (
        db.session.query(LicensesUsers)
        .select_from(Users)
        .join(Users, LicensesUsers.user)
        .filter(Users.id == usr)
        .first()
    )


def cadastro_user(form: dict) -> Literal["Usuário Cadastrado com sucesso!"]:
    """User registration.

    Args:
        form (dict): user info.

    Raises:
        InsertError: If the user tries to insert itself.

    Returns:
        (Literal["Usuário Cadastrado com sucesso!"]): Mensagem de sucesso

    """
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]

        password = form.pop("password")

        usr = Users(**form)
        usr.senhacrip = password
        usr.licenseusr = license_(get_jwt_identity())

        db.session.add(usr)
        db.session.commit()

    except ValueError as e:
        raise InsertError(message=f"Erro ao inserir usuário: {e!s}") from e

    return "Usuário Cadastrado com sucesso!"


def update_user(
    form: dict,
) -> Literal["Informações do usuário atualizadas com sucesso!"]:
    """Update user.

    Args:
        form (dict): user info.

    Raises:
        UpdateError: If the user tries to update itself.

    Returns:
        (Literal["Informações do usuário atualizadas com sucesso!"]): Mensagem de sucesso

    """
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]

        password: str = form.pop("password")

        usr = db.session.query(Users).filter(Users.id == form["id"]).first()

        if password:
            usr.senhacrip = str(password)

        db.session.commit()
    except ValueError as e:
        raise UpdateError(message=f"Erro ao atualizar usuário: {e!s}") from e

    return "Informações do usuário atualizadas com sucesso!"


def delete_user(form: dict) -> Literal["Usuário deletado com sucesso!"]:
    """Delete user.

    Args:
        form (dict): user info.

    Raises:
        DeleteError: If the user tries to delete itself.

    Returns:
        (Literal["Usuário deletado com sucesso!"]): Mensagem de sucesso

    """
    db: SQLAlchemy = app.extensions["sqlalchemy"]

    usr = db.session.query(Users).filter(Users.id == form["id"]).first()

    if usr.id == get_jwt_identity():
        raise DeleteError(
            message="Não é possível deletar seu próprio usuário.",
        )
    db.session.delete(usr)
    db.session.commit()

    return "Usuário deletado com sucesso!"


action = ActionsDict(
    INSERT=cadastro_user,
    UPDATE=update_user,
    DELETE=delete_user,
)


@admin.post("/perform_user")
@jwt_required
async def users() -> Response:
    """Render the users list template.

    Returns:
        Response: HTTP response with rendered template.

    """
    try:
        try:
            form_data = (
                await request.json or await request.data or await request.form
            )

            if isinstance(form_data, (str, bytes)):
                form_data = json.loads(form_data)

            form: DictType = {}
            form.update(form_data)

            method_request: MethodRequested = form.pop("method_request")

            call_act: CallableMethodRequest = action.get(method_request)
            message = call_act(form)

            return await make_response(jsonify(message=message), 200)
        except (InsertError, UpdateError, DeleteError) as e:
            return await make_response(
                jsonify({"message": str(e)}),
                400,
            )

    except ValueError as e:
        app.logger.exception("\n".join(format_exception(e)))
        abort(500, description="Erro interno do servidor")


@admin.get("/usuarios/lista")
async def listagem_usuarios() -> Response:
    """Retorne a lista de usuários vinculados à licença ativa do usuário atual.

    Returns:
        Response: Objeto HTTP contendo a lista de usuários em formato JSON.

    """
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    sess = SessionDict(**{
        k: v for k, v in session.items() if not k.startswith("_")
    })

    token_license = sess["license_object"]["license_token"]

    database = (
        db.session.query(Users)
        .join(LicensesUsers)
        .filter_by(license_token=token_license)
        .all()
    )

    listagem = [
        {
            "id": item.id,
            "login": item.login,
            "nome_usuario": item.nome_usuario,
            "email": item.email,
            "login_time": item.login_time.replace(
                tzinfo=ZoneInfo("America/Manaus"),
            ).strftime("%d/%m/%Y %H:%M:%S"),
            "login_id": item.login_id,
        }
        for item in database
    ]

    jsonified_object = jsonify(database=listagem)
    return await make_response(jsonified_object, 200)
