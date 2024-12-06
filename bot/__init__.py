import multiprocessing as mp
import os
import pathlib

import psutil
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class WorkerThread:

    @property
    def BotStarter(self):  # pragma: no cover

        from .scripts.caixa import caixa
        from .scripts.calculadoras import calculadoras
        from .scripts.elaw import elaw
        from .scripts.esaj import esaj
        from .scripts.pje import pje
        from .scripts.projudi import projudi

        systems = {
            "pje": pje,
            "esaj": esaj,
            "elaw": elaw,
            "caixa": caixa,
            "projudi": projudi,
            "calculadoras": calculadoras,
        }

        return systems.get(self.system)

    # argv: str = None, botname: str = None
    def __init__(self, **kwrgs: dict[str, str]):  # pragma: no cover
        self.kwrgs = kwrgs
        self.__dict__.update(kwrgs)

    def start(self, app: Flask, db: SQLAlchemy) -> int:

        try:

            with app.app_context():

                if not app.testing:  # pragma: no cover

                    from app.models import ThreadBots

                    bot = self.BotStarter
                    pid = os.path.basename(self.path_args.replace(".json", ""))
                    process = mp.Process(
                        target=bot,
                        kwargs=self.kwrgs,
                        name=f"{self.display_name} - {pid}",
                        daemon=False,
                    )

                    process.start()
                    process_id = process.ident

                elif app.testing:  # pragma: no cover

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

    def stop(self, processID: int, pid: str) -> None:

        try:

            sinalizacao = f"{pid}.flag"

            _flag = os.path.join(pathlib.Path(__file__).cwd(), "Temp", pid, sinalizacao)
            path_flag = pathlib.Path(_flag)

            Process = psutil.Process(processID)

            if Process.is_running():
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
