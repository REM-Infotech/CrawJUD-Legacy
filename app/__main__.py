"""Main Entry Point."""

from aether import ThreadPoolWSGIServer

from app import create_app

app = create_app()


server_thread = ThreadPoolWSGIServer(
    host="0.0.0.0",  # noqa: S104
    port=5000,
    app=app,
    poll_interval=0.25,
    max_workers=64,
)

with server_thread as th:
    th.run()
