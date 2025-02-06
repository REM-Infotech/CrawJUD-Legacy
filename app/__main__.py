"""Main entry point for the CrawJUD-Bots application."""

from app import create_app  # noqa: E402

if __name__ == "__main__":
    import logging  # noqa: E402
    import signal  # noqa: E402
    import subprocess  # noqa: S404, E402 # nosec: B404
    import sys  # noqa: E402
    from os import environ, getenv  # noqa: E402
    from platform import system  # noqa: E402

    from dotenv_vault import load_dotenv  # noqa: E402
    from flask import Flask  # noqa: E402
    from gevent.pywsgi import WSGIServer  # noqa: E402
    from geventwebsocket.handler import WebSocketHandler  # noqa: E402

    from git_py import version_file  # noqa: E402

    load_dotenv()

    values = environ.get

    logger = logging.getLogger(__name__)

    def starter(hostname: str, port: int, log_output: bool, app: Flask, **kwargs: dict[str, any]) -> None:
        """Start the application with the specified parameters.

        Args:
            hostname (str): The hostname to listen on.
            port (int): The port to listen on.
            log_output (bool): Whether to log output.
            app (Flask): The Flask application instance.
            **kwargs: Additional keyword arguments.

        """
        # Create a WebSocket

        hostname = kwargs.pop("hostname", hostname)
        port = kwargs.pop("port", port)
        log_output = kwargs.pop("log_output", log_output)
        app = kwargs.pop("app", app)

        wsgi = WSGIServer((hostname, port), app, handler_class=WebSocketHandler, log=app.logger, error_log=app.logger)

        wsgi.serve_forever()

    def handle_exit() -> None:
        """Handle termination signals and exit the program gracefully."""
        sys.exit(0)

    def start_vnc() -> None:
        """Start the TightVNC server with specified parameters."""
        try:
            # Executa o comando com verificação de erro
            subprocess.run(  # noqa: S603 # nosec: B607, B603
                [  # noqa: S607
                    "tightvncserver",
                    ":99",
                    "-geometry",
                    "1600x900",
                    "-depth",
                    "24",
                    "-rfbport",
                    "5999",
                ],
                check=True,  # Lança exceção se o comando falhar
            )
            logger.info("VNC Server started successfully.")
        except Exception:
            ...

    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    def start_app() -> None:
        """Initialize and start the Flask application with SocketIO.

        Sets up the application context, configures server settings,
        and starts the application using specified parameters.

        """
        app, __, _ = create_app()

        args_run: dict[str, str | int | bool] = {}
        app.app_context().push()

        debug = values("DEBUG", "False").lower() == "True"

        hostname = values("SERVER_HOSTNAME", "127.0.0.1") if getenv("INTO_DOCKER", None) else "127.0.0.1"

        # unsafe_werkzeug = getenv("INTO_DOCKER", None) is None or (getenv("DEBUG", "False").lower() == "true")
        port = int(values("PORT", "8000"))
        version_file()
        if system().lower() == "linux":
            start_vnc()

        args_run = {
            "hostname": hostname,
            "debug": debug,
            "port": port,
            "log_output": True,
            "app": app,
        }

        try:
            starter(**args_run)

        except (KeyboardInterrupt, TypeError):
            if system().lower() == "linux":
                try:
                    subprocess.run(["tightvncserver", "-kill", ":99"], check=False)  # noqa: S603, S607 # nosec: B603, B607

                except Exception:
                    # err = traceback.format_exc()
                    # app.logger.exception(err)
                    ...

            sys.exit(0)

    start_app()
