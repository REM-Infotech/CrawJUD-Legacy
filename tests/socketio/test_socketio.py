from flask_socketio import SocketIOTestClient


def test_emit_message(io: SocketIOTestClient):

    io.emit("statusbot", {}, namespace="/log")
    received = io.get_received(namespace="/log")

    assert received is not None
