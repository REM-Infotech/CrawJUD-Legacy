"""Module: getchrome_version.

This module provides functionality to retrieve the installed version of Google Chrome.
"""

from __future__ import annotations

import logging
import platform
import subprocess  # nosec: B404

if platform.system() == "Windows":
    import winreg
from os import popen

logger = logging.getLogger(__name__)


class AnotherChromeVersion:
    """Represent a utility for retrieving the installed Google Chrome version."""

    def get_version(self) -> str:
        """
        Return installed Google Chrome version by executing PowerShell command and parse output.

        Args:
            None.

        Returns:
            str: Chrome version obtained from command output.

        Raises:
            FileNotFoundError: If Google Chrome is not found.

        """
        # Comando do PowerShell
        command = 'scoop info googlechrome | Select-String "Version" | ForEach-Object { ($_ -split ":")[0].Trim() }'

        # Executar o comando no PowerShell
        result = subprocess.run(["powershell.exe", "-Command", command], capture_output=True, text=True, check=False)  # nosec: B603, B607

        # Verificar o resultado
        if result.returncode == 0:
            result = result.stdout.strip()
            v = list(filter(lambda x: "version" in x.lower(), result.split(";")))
            # print(result)
            return v[0].split("=")[-1].strip()

        raise FileNotFoundError("Google Chrome não encontrado.")


class ChromeVersion:
    """Represent a utility for retrieving the installed Google Chrome version."""

    def get_chrome_version(self) -> str | None:
        """
        Return Chrome version string by detecting OS and executing appropriate version lookup.

        Args:
            None.

        Returns:
            str | None: Chrome version if detected, else None.

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
        """
        Traverse Windows registry tree to retrieve key-value pairs from given key path promptly.

        Args:
            keypath (str): The registry key path to traverse.

        Returns:
            dict[str, str]: Registry values as key-value pairs.

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
another_chrome_ver = AnotherChromeVersion().get_version
