import signal
import threading as th
from importlib import import_module
from pathlib import Path
from time import sleep
from typing import Callable, Dict, Tuple, Union

import psutil
from celery import shared_task
from celery.result import AsyncResult
from flask import Flask

process_type = Union[psutil.Process, None]


class BotThread(th.Thread):

    def join(self) -> None:
        th.Thread.join(self)
        if self.exc_bot:
            raise self.exc_bot

    def run(self) -> None:

        self.exc_bot: Exception = None

        try:
            self._target(*self._args, **self._kwargs)
        except BaseException as e:
            self.exc_bot = e


class WorkerThread:

    @staticmethod
    @shared_task(ignore_result=False)
    def start_bot(path_args: str, display_name: str, system: str, typebot: str) -> str:

        try:
            process = BotThread(
                target=WorkerThread,
                args=(
                    path_args,
                    display_name,
                    system,
                    typebot,
                ),
            )

            process.start()
            sleep(2)
            pid = Path(path_args).stem

            if not process.is_alive():
                raise process.join()

            while process.is_alive():

                if signal.SIGTERM:
                    path_flag = (
                        Path(__file__)
                        .cwd()
                        .resolve()
                        .joinpath("exec")
                        .joinpath(pid)
                        .joinpath(f"{pid}.flag")
                    )

                    path_flag.parent.resolve().mkdir(exist_ok=True, mode=0o775)

                    with path_flag.open("w") as f:
                        f.write("Encerrar processo")
                    break

        except Exception as e:
            raise e

        return str("Finalizado!")

    # argv: str = None, botname: str = None
    def __init__(
        self,
        path_args: str,
        display_name: str,
        system: str,
        typebot: str,
        *args: Tuple[str],
        **kwargs: Dict[str, str],
    ) -> None:
        try:

            display_name_ = (
                args[0] if args else kwargs.pop("display_name", display_name)
            )
            path_args_ = args[1] if args else kwargs.pop("path_args", path_args)
            system_ = args[2] if args else kwargs.pop("system", system)
            typebot_ = args[3] if args else kwargs.pop("typebot", typebot)

            kwargs.update({"display_name": display_name})

            bot_: Callable[..., None] = getattr(
                import_module(f".scripts.{system_}", __package__),
                system_,
            )

            bot_(
                **{
                    "display_name": display_name_,
                    "path_args": path_args_,
                    "typebot": typebot_,
                    "system": system_,
                }
            )

        except Exception as e:
            raise e

    def stop(self, processID: int, pid: str, app: Flask = None) -> str:

        try:

            # Process: process_type = None
            # with suppress(psutil.NoSuchProcess):
            #     Process = psutil.Process(processID)

            # if Process and Process.is_running() or app.testing is True:
            #     if not path_flag.exists():

            #         path_flag.parent.resolve().mkdir(parents=True, exist_ok=True)

            #         with open(str(_flag), "w") as f:
            #             f.write("Encerrar processo")

            return f"Process {processID} stopped!"

        except psutil.TimeoutExpired:  # pragma: no cover
            return "O processo não foi encerrado dentro do tempo limite"

        except psutil.NoSuchProcess:  # pragma: no cover
            return f"Process {processID} stopped!"

        except Exception as e:  # pragma: no cover
            return str(e)

    def check_status(self, processID: str) -> str:  # pragma: no cover

        try:

            Process = AsyncResult(processID)
            if Process.status == "SUCCESS":
                return f"Process {processID} stopped!"

            elif Process.status == "FAILURE":
                return "Erro ao inicializar robô"

            return "Process running!"

        except psutil.TimeoutExpired:  # pragma: no cover
            return "O processo não foi encerrado dentro do tempo limite"

        except psutil.NoSuchProcess:  # pragma: no cover
            return f"Process {processID} stopped!"

        except Exception as e:  # pragma: no cover
            return str(e)
