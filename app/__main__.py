"""Main Entry Point."""

from aether import ThreadPoolWSGIServer

from app import create_app, io

app = create_app()


server_thread = ThreadPoolWSGIServer(
    host="0.0.0.0",  # noqa: S104
    port=5002,
    app=app,
    poll_interval=0.25,
    max_workers=64,
)

io.run(app, port=5001, host="0.0.0.0")  # noqa: S104

with server_thread as th:
    th.run()
