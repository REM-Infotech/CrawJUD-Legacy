"""Implement a custom Process subclass for handling bot execution with exception management.

This module provides a specialized Process subclass that captures and properly handles
exceptions that occur during bot execution, allowing for safer concurrent bot operations.

Example:
    bot_thread = BotThread(target=my_bot_function)
    bot_thread.start()
    bot_thread.join()  # Will raise any captured exceptions

"""

from billiard.context import Process


class BotThread(Process):
    """Create a Process subclass that safely manages bot execution and exception handling.

    This class extends the billiard Process class to provide additional exception handling
    capabilities. It captures any exceptions that occur during bot execution and allows
    them to be re-raised in the parent process.

    Attributes:
        exc_bot (Exception): Stores any exception that occurs during bot execution.
            Defaults to None when no exception has occurred.

    """

    exc_bot: Exception = None

    def join(self) -> None:
        """Block until the bot process completes and propagate any captured exceptions.

        Waits for the bot process to finish execution and checks if any exceptions
        occurred. If an exception was captured during execution, it will be re-raised
        in the current process.

        Raises:
            Exception: Any exception that was captured during bot execution.

        """
        Process.join(self)
        if self.exc_bot:
            raise self.exc_bot

    def run(self) -> None:
        """Execute the bot's target function and capture any exceptions that occur.

        Wraps the execution of the target function in a try-except block to capture
        any exceptions that occur during bot operation. Stores captured exceptions
        in the exc_bot attribute.
        """
        self.exc_bot = None

        try:
            self._target(*self._args, **self._kwargs)
        except BaseException as e:
            self.exc_bot = e

    def terminate(self) -> None:
        """Force terminate the bot process immediately."""
        Process.terminate(self)

    def chk_except(self) -> None:
        """Check and raise any exceptions that occurred during bot execution.

        This method allows checking for exceptions without joining the process.
        It should be used when you want to verify the bot's execution state
        without waiting for completion.

        Raises:
            Exception: Any exception that was captured during bot execution.

        """
        if self.exc_bot:
            raise self.exc_bot
