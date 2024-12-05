def test_run_post_bot(client):

    from os import path
    from pathlib import Path

    xls_Test = path.join(Path(__file__).parent.resolve(), "archives", "xls_.xlsx")
    basename = path.basename(xls_Test)
    with Path(xls_Test).open("rb") as f:

        data = {
            "url": "https://",
            "files": {basename: (basename, f)},
            "data": {
                "pid": "V2A5G1",
                "user": "robotz213",
                "xlsx": basename,
                "username": "test",
                "password": "test",
                "login_method": "pw",
                "creds": "test",
                "state": "AM",
            },
        }
    response = client.post("/bot/1/projudi/capa", **{"data": data})
    assert response.status_code == 200
