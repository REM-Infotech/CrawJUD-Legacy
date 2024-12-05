from typing import Any


def test_run_post_bot(client, args_bot: dict[str, str | Any]):

    response = client.post("/bot/1/projudi/capa", **{"data": args_bot})
    assert response.status_code == 200
