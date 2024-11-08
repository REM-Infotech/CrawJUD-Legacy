import os
from app import io
from app import app


from time import time
from time import sleep
from clear import clear
from dotenv import dotenv_values
from multiprocessing import Process
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.misc.checkout import checkout_release_tag

values = dotenv_values()


class ChangeHandler(FileSystemEventHandler):

    last_modified = 0

    def __init__(self, tracked_files):
        super().__init__()
        self.tracked_files = tracked_files

    def on_modified(self, event):
        """Triggered when something is modified."""

        current_time = time()
        # Aguarda 1 segundo para evitar múltiplos eventos
        if current_time - ChangeHandler.last_modified > 3:
            if os.path.basename(event.src_path) == ".version":

                ChangeHandler.last_modified = current_time
                print(
                    f"Mudança detectada no arquivo {event.src_path}, reiniciando o servidor Flask..."
                )
                clear()
                restart_flask()


def start_flask():

    port = int(values.get("PORT", 5000))
    io.run(app, port=int(port))


def flask_Process():

    flask_Process = Process(target=start_flask)
    flask_Process.start()
    return flask_Process


def restart_flask():
    global flask_server_Process
    if flask_server_Process.is_alive():
        flask_server_Process.kill()
        flask_server_Process.join()

    flask_server_Process = flask_Process()
    print("Servidor Flask reiniciado.")


def monitor_changes():

    root_path = os.path.join(os.getcwd())
    tracked_file = os.path.join(os.getcwd(), ".version")
    if not os.path.exists(tracked_file):
        with open(tracked_file, "w") as f:
            f.write("LATEST")

    event_handler = ChangeHandler(tracked_file)
    observer = Observer()
    observer.schedule(
        event_handler,
        path=root_path,
    )
    observer.start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    print("Iniciando monitoramento de mudanças e servidor Flask...")

    with open(".version", "r") as f:
        version = f.read()

    # checkout antes de inicializar

    debug = values.get("DEBUG", "False").lower() in ("true", "1", "t", "y", "yes")
    checkout_release_tag(version, debug)

    # Inicia o servidor Flask
    flask_server_Process = flask_Process()

    # Inicia o monitoramento das mudanças
    monitor_changes()
