import os
from flask import has_app_context
from app import db
from app.models import ThreadBots

from flask import Flask
import threading


class WorkerThread:

    @property
    def BotStarter(self):  # -> Hints:

        from .scripts.pje import pje
        from .scripts.esaj import esaj
        from .scripts.elaw import elaw
        from .scripts.caixa import caixa
        from .scripts.projudi import projudi
        from .scripts.calculadoras import calculadoras

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

    def start(self, app: Flask) -> int:

        try:

            if has_app_context():
                with app.app_context():
                    bot = self.BotStarter
                    pid = os.path.basename(self.path_args.replace(".json", ""))
                    process = threading.Thread(
                        target=bot,
                        kwargs=self.kwrgs,
                        name=f"{self.display_name} - {pid}",
                        daemon=False
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
            path_flag = os.path.join(os.getcwd(), "Temp", pid, sinalizacao)
            with open(path_flag, "w") as f:
                f.write("Encerrar processo")

            for thread in threading.enumerate():
                if thread.ident == processID:
                    thread.join(30)
                    break

            return f"Process {processID} stopped!"

        except Exception:
            return "O processo não foi encerrado dentro do tempo limite"
