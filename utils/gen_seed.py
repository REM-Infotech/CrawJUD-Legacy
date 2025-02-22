"""Provides utility functions for generating unique identifiers and worker names.

This module contains functions for generating unique process identifiers (PIDs) and worker
names using random and secure random number generation. The generated identifiers are
designed to be collision-resistant and follow specific patterns.

Functions:
    worker_name_generator: Generate a unique worker name with prefix and random components.
    generate_pid: Generate a unique process identifier with interleaved letters and digits.
"""

import random
import secrets
import string


def worker_name_generator() -> str:
    """Generate a unique worker name with specific format.

    Creates a worker name by combining a prefix with random uppercase letters and digits
    in the format: 'worker_XXXX_YYYY' where X are letters and Y are digits.

    Returns:
        str: A unique worker identifier in format 'worker_ABCD_1234'.

    Example:
        >>> worker_name_generator()
        'worker_KRTM_5289'

    """
    letters = "".join(secrets.choice(string.ascii_uppercase) for _ in range(4))
    digits = "".join(secrets.choice(string.digits) for _ in range(4))
    prefix = "worker"
    return f"{prefix}_{letters}_{digits}"


def generate_pid() -> str:
    """Generate a unique process identifier with interleaved characters.

    Creates a 6-character string by alternating random uppercase letters and digits.
    Ensures no consecutive repeated characters (avoids patterns like 'AABB').

    Returns:
        str: A 6-character string alternating between letters and digits.

    Example:
        >>> generate_pid()
        'A1B2C3'

    """
    while True:
        # Gerar 4 letras maiúsculas e 4 dígitos
        letters = random.sample(string.ascii_uppercase, 6)
        digits = random.sample(string.digits, 6)

        # Intercalar letras e dígitos
        pid = "".join([letters[i // 2] if i % 2 == 0 else digits[i // 2] for i in range(6)])

        # Verificar se a string gerada não contém sequências do tipo "AABB"
        if not any(pid[i] == pid[i + 1] for i in range(len(pid) - 1)):
            return pid
