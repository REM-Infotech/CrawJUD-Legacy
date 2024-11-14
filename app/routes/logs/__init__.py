from app import app
from flask import abort
from flask_socketio import emit, join_room, Namespace, leave_room

from app.misc import stop_execution
from status.server_side import serverSide
with app.app_context():

    class LogNamespace(Namespace):

        def on_connect(self):
            emit("connected!")

        def on_disconnect(self):
            emit("disconnected!")

        def on_leave(self, data):
            room = data["pid"]
            leave_room(room)

        def on_join(self, data: dict[str, str]):

            room = data["pid"]
            join_room(room)

            # if StatusStop(room) is True:
            #     emit("statusbot", data=data)

            # elif stopped_bot(room) is True:
            #     stop_execution(app, room, True)

        def on_stop_bot(self, data: dict[str, str]):

            pid = data["pid"]
            stop_execution(app, pid, True)
            emit("statusbot", data=data)

        def on_log_message(self, data: dict[str, str]):

            try:
                pid = data["pid"]
                data = serverSide(data, pid)
                emit("log_message", data, room=pid)

            except Exception as e:
                abort(500, description=str(e))
