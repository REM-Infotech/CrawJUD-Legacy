def test_client_flask(client):
    response = client.get("/")
    responses = any([response.status_code == 302, response.status_code == 404])
    assert responses


def test_error_post_bot(client):
    response = client.post("/bot/1/projudi/capa")

    responses = any([response.status_code == 500, response.status_code == 404])
    assert responses
