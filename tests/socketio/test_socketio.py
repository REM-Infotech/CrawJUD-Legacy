from flask_socketio import SocketIOTestClient


def test_connect(io: SocketIOTestClient):

    io.emit("connect", namespace="/log")
    received = io.get_received(namespace="/log")

    message_received = received[-1].get("args") == "connected!"

    assert message_received


def test_join(io: SocketIOTestClient, create_dummy_pid):

    _, pid = create_dummy_pid

    io.emit("join", {"pid": pid}, namespace="/log")
    received = io.get_received(namespace="/log")

    message_received = received[-1].get("args") == f"Joinned room! Room: {pid}"
    assert message_received


def test_disconnect(io: SocketIOTestClient):

    io.emit("disconnect", namespace="/log")
    received = io.get_received(namespace="/log")

    message_received = received[-1].get("args") == "disconnected!"

    assert message_received


def test_leave(io: SocketIOTestClient, create_dummy_pid):

    _, pid = create_dummy_pid

    io.emit("leave", {"pid": pid}, namespace="/log")
    received = io.get_received(namespace="/log")

    message_received = received[-1].get("args") == f"Leaving Room '{pid}'"
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

    message_received = received[-1].get("args") == "Bot stopped!"

    assert message_received


def test_terminate_bot(io: SocketIOTestClient, create_dummy_pid):

    _, pid = create_dummy_pid
    pid = str(pid)

    # With PID
    io.emit("terminate_bot", {"pid": pid}, namespace="/log")
    received = io.get_received(namespace="/log")

    message_received = received[-1].get("args") == "Bot stopped!"

    # Without PID
    io.emit("terminate_bot", {}, namespace="/log")
    received = io.get_received(namespace="/log")

    message_received_ = received[-1].get("args") == "Failed to stop bot!"

    assert message_received and message_received_


def test_log_message(io: SocketIOTestClient, create_dummy_pid):

    _, pid = create_dummy_pid
    pid = str(pid)

    # With PID
    io.emit("log_message", {"pid": pid}, namespace="/log")
    received = io.get_received(namespace="/log")

    message_received = received[-1].get("args") == "message received!"

    # Without PID
    io.emit("log_message", {}, namespace="/log")
    received = io.get_received(namespace="/log")

    message_received_ = received[-1].get("args") == "failed to receive message"

    assert message_received and message_received_
