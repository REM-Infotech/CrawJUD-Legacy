"""
Module for handling bot execution using a custom thread class.

This module defines the BotThread class which extends Process to handle
bot execution with exception capturing.
"""

from billiard.context import Process


class BotThread(Process):
    """
    A BotThread that extends Process to handle bot execution.

    Attributes:
        exc_bot (Exception): Stores any exception raised during execution.

    """

    exc_bot: Exception = None

    def join(self) -> None:
        """
        Wait for the BotThread to finish execution.

        If an exception occurred during execution, it is raised.

        Raises:
            Exception: If an exception occurred during execution.

        """
        Process.join(self)
        # Thread.join(self)
        if self.exc_bot:
            raise self.exc_bot

    def run(self) -> None:
        """
        Run the target function in the BotThread.

        Captures any exceptions raised during execution.
        """
        self.exc_bot = None

        try:
            self._target(*self._args, **self._kwargs)
        except BaseException as e:
            self.exc_bot = e

    def terminate(self) -> None:
        """Terminate the BotThread execution."""
        Process.terminate(self)

    def chk_except(self) -> None:
        """
        Check for exceptions during bot execution.

        If an exception occurred during execution, it is raised.

        Raises:
            Exception: If an exception occurred during execution.

        """
        if self.exc_bot:
            raise self.exc_bot
