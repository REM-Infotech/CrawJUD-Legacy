import debugpy
from aether import ThreadPoolWSGIServer

from app import create_app

debugpy.listen(5678)
debugpy.wait_for_client()  # blocks execution until client is attached
app = create_app()
with ThreadPoolWSGIServer("localhost", 5000, app, max_workers=64) as th:
    th.run()
