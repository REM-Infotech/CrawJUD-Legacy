from typing import Any


def test_client_flask(client, app, args_bot: dict[str, str | Any], create_dummy_pid):
    response_index = client.get("/")
    response_bot_error = client.post("/bot/1/projudi/capa")

    app.debug = True
    response_bot_sucess = client.post("/bot/1/projudi/capa", **{"data": args_bot})

    chk_index = response_index.status_code == 302

    chk_bot_error = response_bot_error.status_code == 500

    chk_bot_success = response_bot_sucess.status_code == 200

    responses = all([chk_index, chk_bot_error, chk_bot_success])

    assert responses
