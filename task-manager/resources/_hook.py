import importlib.abc
import importlib.util
import json
import mimetypes
import sys
from pathlib import Path
from typing import Any

type ModuleType = sys
type MyAny = Any


class JSONLoader(importlib.abc.SourceLoader):
    def get_data(self, path: str) -> str:
        with Path(path).open("r", encoding="utf-8") as f:
            return f.read()

    def get_filename(self, fullname: str) -> str:
        return fullname + ".json"

    def exec_module(self, module: ModuleType) -> None:
        path = Path(module.__spec__.origin)

        if "." in module.__spec__.name:
            path = path.parent.joinpath(
                *module.__spec__.name.split(".")
            ).with_suffix(".json")

        data = json.loads(path.read_text())
        for k, v in data.items():
            setattr(module, k, v)


class JSONFinder(importlib.abc.MetaPathFinder):
    def find_spec(
        self,
        fullname: str,
        path: str,
        target: MyAny = None,
    ) -> ModuleType | None:  # pyright: ignore[reportInvalidTypeForm]
        filename = fullname.split(".")[-1] + ".json"

        path_mod = Path(filename)
        if not path_mod.exists():
            path_mod = Path.cwd().joinpath(filename)

        if not path_mod.exists():
            path_mod = (
                Path(__file__)
                .cwd()
                .joinpath(*fullname.split("."))
                .with_suffix(".json")
            )

        if path_mod.exists() and self.guess(path_mod):
            return importlib.util.spec_from_file_location(
                fullname, filename, loader=JSONLoader()
            )
        return None

    def guess(self, path: Path) -> bool:
        return mimetypes.guess_type(path)[0] == "application/json"


sys.meta_path.append(JSONFinder())
