"""Task execution module."""

import asyncio

from celery import Celery, Task
from flask_sqlalchemy import SQLAlchemy
from quart import Quart
from werkzeug.datastructures.structures import MultiDict

from utils.status import InstanceBot

from ...models import ThreadBots


class TaskExec(InstanceBot):
    """Task execution class."""

    @classmethod
    async def task_exec(
        cls,
        id_: int = None,
        system: str = None,
        typebot: str = None,
        exec_type: str = None,
        app: Quart = None,
        db: SQLAlchemy = None,
        files: MultiDict = None,
        celery_app: Celery = None,
        data_bot: MultiDict = None,
        *args: tuple,
        **kwargs: dict,
    ) -> int:
        """Execute the task with the specified parameters.

        Args:
            app (Quart): The Quart application instance.
            celery_app (Celery): The Celery application instance.
            db (SQLAlchemy): The SQLAlchemy instance.
            id_ (int): The ID of the bot.
            system (str): The system of the bot.
            typebot (str): The type of bot.
            exec_type (str): The type of execution.
            files (MultiDict): The files to process.
            data_bot (MultiDict): The bot data.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        async with app.app_context():
            if exec_type == "start":
                user = data_bot.get("user")
                pid: str = data_bot.get("pid")

                path_pid = await asyncio.create_task(cls.configure_path(app, pid, files))
                data, path_args = await asyncio.create_task(
                    cls.args_tojson(path_pid, pid, id_, system, typebot, data_bot)
                )
                execut, display_name = await asyncio.create_task(cls.insert_into_database(db, data, pid, id_, user))
                try:
                    await asyncio.create_task(cls.send_email(execut, app, "start"))
                except Exception as e:
                    app.logger.error("Error sending email: %s", str(e))

                task: Task = celery_app.send_task(
                    f"bot.{system.lower()}_launcher", args=[str(path_args), display_name, system, typebot]
                )

                process_id = str(task.id)

                # Salva o ID no "banco de dados"
                add_thread = ThreadBots(pid=pid, processID=process_id)
                db.session.add(add_thread)
                db.session.commit()

                return 200

            elif exec_type == "stop":
                pid = data_bot.get("pid")
                db: SQLAlchemy = app.extensions["sqlalchemy"]
                status = data_bot.get("status")
                filename = await asyncio.create_task(cls.make_zip(pid))
                execut = await asyncio.create_task(cls.send_stop_exec(app, db, pid, status, filename))

                try:
                    await asyncio.create_task(cls.send_email(execut, app, "stop"))
                except Exception as e:
                    app.logger.error("Error sending email: %s", str(e))

                return 200

        return 500
