"""Main entry point for the server application."""

from tqdm import tqdm

from server import MasterApp

if __name__ == "__main__":
    application_instance = MasterApp()
    try:
        application_instance.prompt()

    except KeyboardInterrupt:
        tqdm.write("Stopping app")
        application_instance.thead_io.join(10)
