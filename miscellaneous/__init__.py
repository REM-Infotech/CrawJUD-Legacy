import importlib
import sys


def reload_module(module_name: str) -> None:  # pragma: no cover
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    else:
        importlib.import_module(module_name)
