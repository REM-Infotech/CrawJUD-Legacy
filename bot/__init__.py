import os
import sys
import pathlib
import subprocess
from time import sleep
from flask import has_app_context

from flask import Flask
import multiprocessing as mp
import psutil


class WorkerThread:

    # argv: str = None, botname: str = None
    def __init__(self, **kwrgs: dict[str, str]):
        self.kwrgs = kwrgs
        self.__dict__.update(kwrgs)

    def start(self, app: Flask) -> int:

        try:
            from app.models import ThreadBots
            from app import db

            if has_app_context():
                with app.app_context():

                    if mp.get_start_method(allow_none=True) != "spawn":
                        mp.set_start_method("spawn")

                    pid = os.path.basename(self.path_args.replace(".json", ""))

                    args_parse = []
                    for arg, value in self.kwrgs.items():
                        args_parse.append([f"--{arg}", f"{value}"])

                    executable = os.path.join(os.getcwd(), "run.py")

                    python_path = os.path.join(sys.executable)

                    cmd = [python_path, executable]
                    for argument in args_parse:
                        cmd.extend(argument)

                    subprocess.run(cmd)
                    sleep(2)
                    os_pid = os.path.join(
                        self.kwrgs.get("path_args"),
                        f"OS_PID {self.kwrgs.get("pid")}.txt",
                    )
                    while not pathlib.Path(os_pid).exists():
                        pass

                    with open(os_pid, "r") as f:
                        process_id = f.read()
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

                Process.wait(60)

            return f"Process {processID} stopped!"

        except psutil.TimeoutExpired:
            return "O processo não foi encerrado dentro do tempo limite"

        except psutil.NoSuchProcess:
            return f"Process {processID} stopped!"

        except Exception as e:
            return str(e)
