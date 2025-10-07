"""Main Entry Point."""

import debugpy  # noqa: T100
from aether import ThreadPoolWSGIServer

from app import create_app

debugpy.listen(5678)  # noqa: T100
debugpy.wait_for_client()  # noqa: T100

app = create_app()


with ThreadPoolWSGIServer("localhost", 5000, app, max_workers=64) as th:
    th.run()
