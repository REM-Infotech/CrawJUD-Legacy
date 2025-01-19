import pathlib

# from contextlib import suppress
from importlib import import_module
from typing import Callable, Union

import psutil
from celery.result import AsyncResult
from flask import Flask

# from memory_profiler import profile

process_type = Union[psutil.Process, None]

# fp = open("memory_profiler.log", "+w")


class WorkerThread:

    # @profile(stream=fp)
    @property
    def BotStarter(self) -> Callable[[], None]:  # pragma: no cover

        return getattr(
            import_module(f".scripts.{self.system}", __package__),
            self.system,
        )

    # argv: str = None, botname: str = None
    def __init__(self, **kwrgs: dict[str, str]):  # pragma: no cover
        self.kwrgs = kwrgs
        self.__dict__.update(kwrgs)

    # @profile
    def start(self) -> None:

        try:

            self.BotStarter(**self.kwrgs)

        except Exception as e:
            raise e

    def stop(self, processID: int, pid: str, app: Flask = None) -> str:

        try:

            path_flag = (
                pathlib.Path(__file__)
                .cwd()
                .resolve()
                .joinpath("exec")
                .joinpath(pid)
                .joinpath(f"{pid}.flag")
            )

            path_flag.parent.resolve().mkdir(exist_ok=True, mode=775)

            with path_flag.open("w") as f:
                f.write("Encerrar processo")

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
