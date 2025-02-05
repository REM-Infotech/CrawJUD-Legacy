"""Module: getchromeVer.

This module provides functionality to retrieve the installed version of Google Chrome.
"""  # noqa: N999

from __future__ import annotations

import logging
import platform

if platform.system() == "Windows":
    import winreg
from os import popen

logger = logging.getLogger(__name__)


class ChromeVersion:
    """Represent a utility for retrieving the installed Google Chrome version."""

    def get_chrome_version(self) -> str | None:
        """Return the version of Google Chrome installed on the system, or None if undetected.

        This method determines the operating system and retrieves the version
        of Google Chrome accordingly. For Windows, it attempts to read the
        version from the registry. For macOS and Linux, it uses the command
        line to get the version.

        Returns:
            str: The version of Google Chrome installed on the system, or None
            if the version could not be determined.

        """
        result = None
        system = platform.system()
        if system == "Windows":
            # Try registry key.
            key_path = r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome"
            return self.traverse_registry_tree(keypath=key_path).get("Version")

        if system.upper() == "DARWIN":
            result = popen(  # noqa: S605 # nosec: B605
                r"/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version",
            ).read()

        elif system.upper() == "LINUX":
            result = popen("/usr/bin/google-chrome --version").read()  # noqa: S605 # nosec: B605

        if result:
            result = result.removeprefix("Google Chrome ")
            result = str(result).strip()

        return result

    def traverse_registry_tree(self, keypath: str) -> dict[str, str]:
        """Return a dictionary of registry values from the given key path on Windows.

        Args:
            keypath (str): The registry key path to traverse.

        Returns:
            dict[str, str]: A dictionary containing the registry values.

        """
        hkey = winreg.HKEY_LOCAL_MACHINE
        reg_dict = {}
        with winreg.OpenKey(hkey, keypath, 0, winreg.KEY_READ) as key:
            _, num_values, _ = winreg.QueryInfoKey(key)

            for i in range(num_values):
                value_name, value_data, _ = winreg.EnumValue(key, i)
                reg_dict.update({value_name: value_data})

        return reg_dict


chrome_ver = ChromeVersion().get_chrome_version

if __name__ == "__main__":
    logger.info(f"Google Chrome version: {chrome_ver()}")  # noqa: G004
