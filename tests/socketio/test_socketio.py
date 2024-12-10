from flask_socketio import SocketIOTestClient


def test_connect(io: SocketIOTestClient):

    io.emit("connect", namespace="/log")
    received = io.get_received(namespace="/log")

    message_received = str(received[-1].get("args")) == "connected!"

    assert message_received


def test_disconnect(io: SocketIOTestClient):

    io.emit("disconnect", namespace="/log")
    received = io.get_received(namespace="/log")

    message_received = str(received[-1].get("args")) == "disconnected!"

    assert message_received


def test_leave(io: SocketIOTestClient, create_dummy_pid):

    _, pid = create_dummy_pid

    io.emit("leave", {"pid": pid}, namespace="/log")
    received = io.get_received(namespace="/log")

    message_received = str(received[-1].get("args")) == f"Leaving Room '{pid}'"
    assert message_received


def test_statusbot(io: SocketIOTestClient):

    io.emit("statusbot", {}, namespace="/log")
    received = io.get_received(namespace="/log")

    assert received is not None


def test_stop_bot(io: SocketIOTestClient, create_dummy_pid):

    _, pid = create_dummy_pid
    pid = str(pid)

    io.emit("stop_bot", {"pid": pid}, namespace="/log")
    received = io.get_received(namespace="/log")

    message_received = str(received[-1].get("args")) == "Bot stopped!"

    assert message_received


def test_terminate_bot(io: SocketIOTestClient, create_dummy_pid):

    _, pid = create_dummy_pid
    pid = str(pid)

    # With PID
    io.emit("terminate_bot", {"pid": pid}, namespace="/log")
    received = io.get_received(namespace="/log")

    message_received = str(received[-1].get("args")) == "Bot stopped!"

    # Without PID
    io.emit("terminate_bot", {}, namespace="/log")
    received = io.get_received(namespace="/log")

    message_received_ = str(received[-1].get("args")) == "Failed to stop bot!"

    assert message_received and message_received_


def test_join_and_message(io: SocketIOTestClient, create_dummy_pid):
    """Teste do endpoint Websocket "log_message"

    Args:
        io (SocketIOTestClient): Cliente Socketio
        create_dummy_pid (tuple[str, str]): Execução dummy
    """
    user, pid = create_dummy_pid
    pid = str(pid)
    print(pid)
    data: dict[str, str | int] = {
        "message": "Mensagem Teste",
        "pid": str(pid),
        "type": "log",
        "pos": 15,
        "graphicMode": "doughnut",
        "total": 15,
        "system": "projudi",
        "typebot": "capa",
    }

    # First join without cached pid in Redis
    io.emit("join", {"pid": pid}, namespace="/log")
    received = io.get_received(namespace="/log")

    message_received_notCache = (
        str(received[-1].get("args")) == f"Joinned room! Room: {pid}"
    )

    # With PID
    io.emit("log_message", data, namespace="/log")
    received = io.get_received(namespace="/log")
    print(received)

    message_received = str(received[-1].get("args")) == "message received!"

    # Second join with cached pid in Redis
    io.emit("join", {"pid": pid}, namespace="/log")
    received = io.get_received(namespace="/log")

    message_received_Cache = (
        str(received[-1].get("args")) == f"Joinned room! Room: {pid}"
    )

    # Without PID
    io.emit("log_message", {}, namespace="/log")
    received = io.get_received(namespace="/log")

    message_received_ = str(received[-1].get("args")) == "failed to receive message"

    assert all(
        [
            message_received,
            message_received_,
            message_received_notCache,
            message_received_Cache,
        ]
    )
