import multiprocessing as mp
import os
import pathlib

import psutil
from flask import Flask, has_app_context
from flask_sqlalchemy import SQLAlchemy


class WorkerThread:

    @property
    def BotStarter(self):  # -> Hints:

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
    def __init__(self, **kwrgs: dict[str, str]):
        self.kwrgs = kwrgs
        self.__dict__.update(kwrgs)

    def start(self, app: Flask, db: SQLAlchemy) -> int:

        try:
            from app.models import ThreadBots

            if has_app_context():
                with app.app_context():
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
            path_flag = pathlib.Path(
                os.path.join(os.getcwd(), "Temp", pid, sinalizacao)
            )

            Process = psutil.Process(processID)

            if Process.is_running():
                if not path_flag.exists():
                    with open(str(path_flag), "w") as f:
                        f.write("Encerrar processo")

            return f"Process {processID} stopped!"

        except psutil.TimeoutExpired:
            return "O processo não foi encerrado dentro do tempo limite"

        except psutil.NoSuchProcess:
            return f"Process {processID} stopped!"

        except Exception as e:
            return str(e)
