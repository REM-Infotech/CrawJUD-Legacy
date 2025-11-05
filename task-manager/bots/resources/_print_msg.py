import builtins


class CustomPrint[T]:
    def __init__(self, new_print: T) -> None:
        self.new_print = new_print

    def __enter__(self) -> None:
        self._old_print = builtins.print
        builtins.print = self.new_print

    def __exit__(self, *args) -> None:
        builtins.print = self._old_print
