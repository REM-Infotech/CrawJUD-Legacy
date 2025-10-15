"""Main Entry Point."""

from aether import ThreadPoolWSGIServer

from app import create_app

app = create_app()

with ThreadPoolWSGIServer(
    host="0.0.0.0",  # noqa: S104 # pyright: ignore[reportArgumentType]
    port=5000,
    app=app,
    poll_interval=0.25,
    max_workers=64,
) as th:
    th.run()
