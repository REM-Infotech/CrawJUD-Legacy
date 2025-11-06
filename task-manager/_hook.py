import importlib.abc
import importlib.util
import json
import mimetypes
import sys
import weakref
from pathlib import Path
from types import MethodType
from typing import Any

from packaging.version import parse

type ModuleType = sys
type MyAny = Any


class Legacy(importlib.abc.SourceLoader):
    def get_data(self, path: str) -> str:
        with Path(path).open("r", encoding="utf-8") as f:
            return f.read()

    def get_filename(self, fullname: str) -> str:
        return fullname + ".json"

    def exec_module(self, module: ModuleType) -> None:
        setattr(module, "_saferef", self.safe_ref)  # noqa: B010
        setattr(module, "parse_version", parse)  # noqa: B010

    def safe_ref(self, target: MyAny) -> MyAny:
        """Implementa referência fraca segura para funções e métodos.

        Args:
            target (types.FunctionType | types.MethodType): Função ou método alvo

        Returns:
            callable: Função que retorna o alvo se ainda existir, senão None

        """
        # Se for método, use WeakMethod
        if isinstance(target, MethodType):
            ref = weakref.WeakMethod(target)
        else:
            ref = weakref.ref(target)
        return ref


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
                *module.__spec__.name.split("."),
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
                fullname,
                filename,
                loader=JSONLoader(),
            )

        if fullname == "blinker._saferef":
            return importlib.util.spec_from_loader(
                fullname,
                loader=Legacy(),
            )

        if fullname.startswith("pkg_resources"):
            return importlib.util.spec_from_loader(
                fullname,
                loader=Legacy(),
            )

        return None

    def guess(self, path: Path) -> bool:
        return mimetypes.guess_type(path)[0] == "application/json"


# Insere o JSONFinder na primeira posição do sys.meta_path para interceptar
# todas as tentativas de importação antes dos outros finders padrão do Python.
# Isso garante que até instruções como "from module import object" sejam capturadas.
sys.meta_path.insert(0, JSONFinder())
sys.meta_path.insert(1, JSONFinder())
# Limpa o cache de importação para garantir que as alterações no meta_path sejam
# reconhecidas imediatamente.
importlib.invalidate_caches()
