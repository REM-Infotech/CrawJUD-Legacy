from .message import PrintBot  # noqa:D100


class SendMessage(PrintBot):
    """Handle sending messages via SocketBot."""

    def setup_message(self) -> None:
        """Set up the message to be sent by the bot.

        Args:
            message (str): The message to be sent by the bot.

        """

    def insert_redis(self) -> None:
        """Empty."""

    def send_message(self) -> None:
        """Empty."""
