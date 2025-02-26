"""Function to convert a string value to the appropriate type."""

import json
from contextlib import suppress

from git import Union

ValueTypes = Union[str, int, float, bool, dict, list]


def convert_to_type(val: str) -> ValueTypes:
    """Convert a string value to the appropriate type."""
    with suppress(ValueError):
        return int(val)

    with suppress(ValueError):
        return float(val)

    if val.lower() == "true":
        return True

    if val.lower() == "false":
        return False

    with suppress(json.JSONDecodeError, TypeError, Exception):
        return json.loads(val)

    return val
