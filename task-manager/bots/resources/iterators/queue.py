"""Implemente iteradores para filas do tipo Queue.

Este módulo fornece o iterador QueueIterator para acesso
sequencial aos elementos de uma fila, tratando exceções
de fila vazia ou encerrada.
"""

from queue import Empty, Queue, ShutDown
from typing import Self


class QueueIterator[T]:
    """Implemente iterador para filas do tipo Queue.

    Permite acesso sequencial aos elementos da fila,
    tratando exceções de fila vazia ou encerrada.
    """

    def __init__(self, queue: Queue) -> None:
        """Inicialize o iterador com a fila fornecida.

        Args:
            queue (Queue): Fila a ser iterada.

        """
        self._queue = queue

    def __iter__(self) -> Self:
        """Retorne o próprio iterador.

        Returns:
            Self: O próprio iterador.

        """
        return self

    def __next__(self) -> T:
        """Retorne o próximo elemento da fila ou None se vazia.

        Returns:
            T: Próximo elemento da fila ou None se vazia.

        Raises:
            StopIteration: Se a fila estiver encerrada.

        """
        data = None
        try:
            data = self._queue.get_nowait()

        except Empty:
            data = None

        except ShutDown:
            raise StopIteration from None

        return data
