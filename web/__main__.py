"""Entry point for the CrawJUD-Web Quart application.

This module loads environment variables, initializes the app, and starts the server.
"""

import subprocess
from os import environ, getenv

from clear import clear
from dotenv_vault import load_dotenv

load_dotenv()

if __name__ == "__main__":
    from web import create_app

    app = create_app()
    clear()
    port = int(environ.get("PORT", 5000))
    hostname = getenv(
        "SERVER_HOSTNAME",
        subprocess.run(
            [
                "powershell",
                "hostname",
            ],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip(),
    )

    debug = getenv("DEBUG", "False").lower() == "true"
    into_prod = getenv("INTO_PRODUCTION", "False")

    # wsgi_app = create_server(
    #     app,
    #     host=hostname,
    #     port=port,
    #     threads=4,
    #     connection_limit=100,
    #     cleanup_interval=30,
    #     max_request_body_size=10 * 1024 * 1024,
    # )
    # wsgi_app.run()
    app.run(host=hostname, port=port, debug=debug)
