from aether import ThreadPoolWSGIServer

from app import create_app

app = create_app()
with ThreadPoolWSGIServer("localhost", 5000, app, max_workers=64) as th:
    th.run()
