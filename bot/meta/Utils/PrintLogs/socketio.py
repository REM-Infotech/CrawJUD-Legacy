from app import io
from app import app


class SocketBot:

    def with_context(self, event: str, data: dict):

        with app.app_context():
            io.emit(event, data, namespace="/log")

    def send_message(self, data: dict[str, str | int], url):

        self.with_context("log_message", data)

    def end_message(self, data: dict, url):

        self.with_context("stop_bot", data)
