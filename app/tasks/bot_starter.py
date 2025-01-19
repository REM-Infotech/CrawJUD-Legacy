import eventlet  # noqa: E402

eventlet.monkey_patch(socket=True)  # noqa: E402
import debugpy
from celery import shared_task
from flask import current_app as app

from bot import WorkerThread

# from pathlib import Path


@shared_task(ignore_result=False)
def init_bot(
    path_args: str, display_name: str, system: str, typebot: str, *args, **kwargs
) -> None:

    if app.debug is True:
        debugpy.listen(5678)
        debugpy.wait_for_client()

    worker_thread = WorkerThread(
        path_args=path_args,
        display_name=display_name,
        system=system,
        typebot=typebot,
    )
    worker_thread.start()
