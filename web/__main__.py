"""Entry point for the CrawJUD-Web Flask application.

This module loads environment variables, initializes the app, and starts the server.
"""

import subprocess
from os import environ, getenv

from clear import clear
from dotenv_vault import load_dotenv
from git_py import version_file  # noqa: F401

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
    # if into_prod == "True":
    #     wsgi = WSGIServer(
    #         (hostname, port),
    #         app,
    #         error_log=app.logger,
    #         log=app.logger,
    #     )
    #     wsgi.serve_forever()

    # elif into_prod == "False":
    app.run(hostname, port, debug)
