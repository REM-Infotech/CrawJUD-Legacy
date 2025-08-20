"""Modulo de gerenciamento de tarefas do Celery."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

from crawjud import bots
from crawjud.api import create_app
from crawjud.decorators import shared_task
from crawjud.models.bots import BotsCrawJUD, Executions
from crawjud.models.users import LicensesUsers, Users
from crawjud.tasks import files, mail, message

if TYPE_CHECKING:
    from collections.abc import Generator

    from flask_sqlalchemy import SQLAlchemy

__all__ = ["bots", "files", "mail", "message"]


def _query_info(
    db: SQLAlchemy,
    bot_execution_id: str,
    pid: str,
) -> tuple[BotsCrawJUD | None, Executions | None]:
    bot = (
        db.session.query(BotsCrawJUD)
        .filter(BotsCrawJUD.id == bot_execution_id)
        .first()
    )
    exc = db.session.query(Executions).filter(Executions.pid == pid).first()

    return (bot, exc)


def _query_user_license(
    db: SQLAlchemy,
    user_id: str,
    license_token: str,
) -> tuple[Users | None, LicensesUsers | None]:
    usr = db.session.query(Users).filter(Users.id == user_id).first()
    license_ = (
        db.session.query(LicensesUsers)
        .filter(LicensesUsers.license_token == license_token)
        .first()
    )

    return usr, license_


@shared_task(name="crawjud.save_database")
async def save_database(
    pid: str,
    bot_execution_id: str,
    arquivo_xlsx: str = "Sem Arquivo",
    signal: str = "start",
    status: str = "Em Execução",
    user_id: str | None = None,
    license_token: str | None = None,
    file_output: str | None = None,
    total_rows: int | None = None,
) -> None:
    """Salva o estado atual do banco de dados."""
    app = await create_app()
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    async with app.app_context():
        bot, exc = _query_info(db, bot_execution_id=bot_execution_id, pid=pid)
        now_ = datetime.now(tz=ZoneInfo("America/Manaus"))

        def iter_admins(
            usrs_admins: list[Users],
        ) -> Generator[Users, Any, None]:
            yield from usrs_admins

        if license_token and user_id and not exc:
            usr_, license_ = _query_user_license(
                db=db,
                user_id=user_id,
                license_token=license_token,
            )

            exc = Executions()
            exc.pid = pid
            exc.status = status
            exc.arquivo_xlsx = arquivo_xlsx
            exc.file_output = "Aguardando Arquivo"
            exc.bot_id = bot.id
            exc.user_id = usr_.id
            exc.data_execucao = now_
            exc.data_finalizacao = now_
            exc.license_id = license_.id

            db.session.add(exc)

            if all([exc, file_output, total_rows]):
                exc.data_finalizacao = now_
                exc.file_output = file_output

        else:
            usr_: Users = exc.user
            license_: LicensesUsers = exc.license_usr

        cc = []
        if not usr_.admins:
            cc.extend([
                user_admin.email for user_admin in iter_admins(license_.admins)
            ])

        mail.send_email.apply_async(
            kwargs={
                "bot_name": bot.display_name,
                "user_name": usr_.nome_usuario,
                "email_target": usr_.email,
                "email_type": signal,
            },
        )

        db.session.commit()
