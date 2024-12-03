import platform

if platform.system() == "Windows":
    import winreg
from os import popen

inst_OS: dict[str, dict[str, list]] = {
    "DARWIN": {
        "PATH": r"/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"
    },
    "LINUX": {"PATH": "/usr/bin/google-chrome"},
}


class ChromeVersion:

    def get_chrome_version(self):
        """Gets the Chrome version."""

        cmd = "/usr/bin/google-chrome --version"
        system = platform.system()
        if system == "Windows":
            # Try registry key.
            key_path = r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome"
            return self.traverse_registry_tree(keypath=key_path).get("Version")

        path = inst_OS.get(system).get("PATH")
        cmd = path + " --version"
        result = popen(cmd).read()
        if result:
            result = str(result.strip("Google Chrome ").strip())

        return result

    def traverse_registry_tree(self, keypath: str) -> dict[str, str]:

        hkey = winreg.HKEY_LOCAL_MACHINE
        reg_dict = {}
        with winreg.OpenKey(hkey, keypath, 0, winreg.KEY_READ) as key:
            num_subkeys, num_values, last_modified = winreg.QueryInfoKey(key)

            for i in range(0, num_values):
                value_name, value_data, value_type = winreg.EnumValue(key, i)
                reg_dict.update({value_name: value_data})

        return reg_dict


chrome_ver = ChromeVersion().get_chrome_version

if __name__ == "__main__":
    print(chrome_ver())
