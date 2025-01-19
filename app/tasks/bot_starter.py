from celery import shared_task

# from pathlib import Path


@shared_task(ignore_result=False)
def init_bot(arg) -> None:

    return "Sucess"
