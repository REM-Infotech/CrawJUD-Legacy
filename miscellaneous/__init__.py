"""Module: miscellaneous.

This module provides miscellaneous utility functions.
"""

import importlib
import sys


def reload_module(module_name: str) -> None:
    """Reload a module by its name.

    If the module is already loaded, it will be reloaded. Otherwise, it will be imported.

    Args:
        module_name (str): The name of the module to reload.

    """
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    else:
        importlib.import_module(module_name)
