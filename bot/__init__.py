from __future__ import annotations

import multiprocessing as mp
import os
import pathlib
from contextlib import suppress
from importlib import import_module
from typing import Union

import psutil
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# from memory_profiler import profile

process_type = Union[psutil.Process, None]

# fp = open("memory_profiler.log", "+w")


class WorkerThread:

    # @profile(stream=fp)
    def BotStarter(
        self,
    ) -> Union[projudi, elaw, calculadoras, caixa, esaj, pje]:

        return getattr(
            import_module(f".scripts.{self.system}", __package__),
            self.system,
        )

    # argv: str = None, botname: str = None
    def __init__(self, **kwrgs: dict[str, str]) -> None:
        self.kwrgs = kwrgs
        self.__dict__.update(kwrgs)

    # @profile
    def start(self, app: Flask, db: SQLAlchemy) -> int:

        try:

            with app.app_context():

                from app.models import ThreadBots

                pid = os.path.basename(self.path_args.replace(".json", ""))

                if not app.testing:

                    bot = self.BotStarter()
                    process = mp.Process(
                        target=bot,
                        kwargs=self.kwrgs,
                        name=f"{self.display_name} - {pid}",
                        daemon=False,
                    )

                    process.start()
                    process_id = process.ident

                elif app.testing:

                    import random
                    import string

                    digits = random.sample(string.digits, 6)
                    process_id = "".join(digits)

                # Salva o ID no "banco de dados"
                add_thread = ThreadBots(pid=pid, processID=process_id)
                db.session.add(add_thread)
                db.session.commit()
                return 200

        except Exception:
            return 500

    def stop(self, processID: int, pid: str, app: Flask = None) -> str:

        try:

            sinalizacao = f"{pid}.flag"

            _flag = os.path.join(pathlib.Path(__file__).cwd(), "exec", pid, sinalizacao)
            path_flag = pathlib.Path(_flag)

            Process: process_type = None
            with suppress(psutil.NoSuchProcess):
                Process = psutil.Process(processID)

            if Process and Process.is_running() or app.testing is True:
                if not path_flag.exists():

                    path_flag.parent.resolve().mkdir(parents=True, exist_ok=True)

                    with open(str(_flag), "w") as f:
                        f.write("Encerrar processo")

            return f"Process {processID} stopped!"

        except psutil.TimeoutExpired:
            return "O processo não foi encerrado dentro do tempo limite"

        except psutil.NoSuchProcess:
            return f"Process {processID} stopped!"

        except Exception as e:
            return str(e)

    def check_status(self, processID: int) -> str:

        try:

            Process = psutil.Process(processID)

            if Process:
                return "Process running!"

            return f"Process {processID} stopped!"

        except psutil.TimeoutExpired:
            return "O processo não foi encerrado dentro do tempo limite"

        except psutil.NoSuchProcess:
            return f"Process {processID} stopped!"

        except Exception as e:
            return str(e)


if __name__ == "__main__":

    from .scripts import caixa, calculadoras, elaw, esaj, pje, projudi
