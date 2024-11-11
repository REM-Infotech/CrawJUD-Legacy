import os
from flask import has_app_context
from app import db, app
from app.models import ThreadBots

import psutil
from typing import Union
import multiprocessing as mp

# Bots

from .scripts.pje import pje
from .scripts.esaj import esaj
from .scripts.elaw import elaw
from .scripts.caixa import caixa
from .scripts.projudi import projudi
from .scripts.calculadoras import calculadoras

Hints = Union[pje, esaj, elaw, caixa, projudi, calculadoras]


class WorkerThread:

    @property
    def BotStarter(self):  # -> Hints:

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

    def start(self) -> int:

        try:

            bot = self.BotStarter
            pid = os.path.basename(self.path_args.replace(".json", ""))
            process = mp.Process(
                target=bot,
                kwargs=self.kwrgs,
                name=f"{self.display_name} - {pid}",
            )
            process.start()
            process_id = process.ident

            if has_app_context():
                with app.app_context():

                    # Salva o ID no "banco de dados"
                    add_thread = ThreadBots(pid=pid, processID=process_id)
                    db.session.add(add_thread)
                    db.session.commit()
                    return 200

        except Exception as e:
            print(e)
            return 500

    def stop(self, processID: int, pid: str) -> None:

        try:

            sinalizacao = f"{pid}.flag"
            processo = psutil.Process(processID)
            path_flag = os.path.join(os.getcwd(), "Temp", pid, sinalizacao)
            with open(path_flag, "w") as f:
                f.write("Encerrar processo")

            processo.wait(60)

            return f"Process {processID} stopped!"

        except psutil.TimeoutExpired:
            return "O processo não foi encerrado dentro do tempo limite"

        except psutil.NoSuchProcess:
            return f"Process {processID} stopped!"
