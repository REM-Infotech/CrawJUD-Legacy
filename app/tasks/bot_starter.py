import eventlet

eventlet.monkey_patch(socket=True)
import importlib
import sys

from celery import shared_task

from bot import WorkerThread

# from flask import current_app as app


# from pathlib import Path
def reload_module(module_name: str) -> None:  # pragma: no cover
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    else:
        importlib.import_module(module_name)


@shared_task(ignore_result=False)
def init_bot(
    path_args: str,  # path json with arguments
    display_name: str,  # bot Name
    system: str,  # bot portal
    typebot: str,  # type bot
    *args,
    **kwargs
) -> str:

    try:

        reload_module("bot")
        worker_thread = WorkerThread(
            path_args=path_args,
            display_name=display_name,
            system=system,
            typebot=typebot,
        )
        worker_thread.start()

        return "Finalizado!"

    except Exception as e:
        raise e
