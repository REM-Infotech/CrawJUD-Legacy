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

    result_sucess: list[bool] = []
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

    def cache_testing():
        # First join without cached pid in Redis
        io.emit("join", {"pid": pid}, namespace="/log")
        received = io.get_received(namespace="/log")

        message_received_notCache = (
            str(received[-1].get("args")) == f"Joinned room! Room: {pid}"
        )

        # With PID
        io.emit("log_message", data, namespace="/log")
        received = io.get_received(namespace="/log")

        message_received = str(received[-1].get("args")) == "message received!"

        # Second join with cached pid in Redis
        io.emit("join", {"pid": pid}, namespace="/log")
        received = io.get_received(namespace="/log")

        message_received_Cache = (
            str(received[-1].get("args")) == f"Joinned room! Room: {pid}"
        )

        result_sucess.extend(
            [message_received_notCache, message_received, message_received_Cache]
        )

    def pos_testing():
        # Test POS == 0
        data_pos0 = data
        data_pos0.update({"pos": 0})
        io.emit("log_message", data_pos0, namespace="/log")
        received = io.get_received(namespace="/log")

        message_received_pos0 = str(received[-1].get("args")) == "message received!"

        # Test POS == 1
        data_pos1 = data
        data_pos1.update({"pos": 1})
        io.emit("log_message", data_pos1, namespace="/log")
        received = io.get_received(namespace="/log")

        message_received_pos1 = str(received[-1].get("args")) == "message received!"

        result_sucess.extend([message_received_pos0, message_received_pos1])

    def error_testing():
        # Without PID
        io.emit("log_message", {}, namespace="/log")
        received = io.get_received(namespace="/log")

        message_received_ = str(received[-1].get("args")) == "failed to receive message"
        result_sucess.append(message_received_)

    def datatype_testing():

        data_error = {}
        data_success = {}
        data_graphic = {}

        data_error.update(data)
        data_success.update(data)
        data_graphic.update(data)

        data_error.update({"type": "error", "pos": data["pos"] + 1})
        data_success.update({"type": "success"})
        data_graphic.update({"graphicMode": "bar", "type": "info"})

        # Test message_type == error
        io.emit("log_message", data_error, namespace="/log")
        received = io.get_received(namespace="/log")
        result1 = str(received[-1].get("args")) == "message received!"

        # Test message_type == "success"
        io.emit("log_message", data_success, namespace="/log")
        received = io.get_received(namespace="/log")
        result2 = str(received[-1].get("args")) == "message received!"

        # Test graphic_mode == "doughnut" and message_type == info
        io.emit("log_message", data_graphic, namespace="/log")
        received = io.get_received(namespace="/log")
        result3 = str(received[-1].get("args")) == "message received!"

        result_sucess.extend([result1, result2, result3])

    cache_testing()
    pos_testing()
    error_testing()
    datatype_testing()

    assert all(result_sucess)
