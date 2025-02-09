"""Module for logs routes."""

from importlib import import_module

import_module(".logs", package=__package__)
import_module(".execution", package=__package__)
