"""Main entry point for the server application."""

import os
import sys

from crawjud.core.main import main_server

if __name__ == "__main__":
    if "debugpy" in sys.modules:
        os.environ["DEBUG"] = "True"

    SystemExit(main_server())
