import os
import pathlib
import zipfile
from datetime import datetime
from os import path
from pathlib import Path
from shutil import rmtree

import pytz


def makezip(pid: str) -> str:  # pragma: no cover

    file_paths = []
    exec_path = (
        Path(pathlib.Path(__file__).cwd().resolve()).joinpath("exec").joinpath(pid)
    )

    exec_path.mkdir(mode=775, exist_ok=True)
    for root, dirs, files in exec_path.walk():
        if "chrome" in str(root) and root.is_dir():
            rmtree(root, ignore_errors=True)

        elif "chrome" in str(root) and root.is_file():
            root.unlink()

        elif "json" in root.suffix or "flag" in root.suffix:
            root.unlink()

    files = [str(f) for f in exec_path.iterdir() if f.is_file() and pid in f.stem]
    files_subfolders = [
        path.join(f, file)
        for f in [str(f) for f in exec_path.iterdir() if f.is_dir() and pid in f.stem]
        for file in Path(f).iterdir()
        if Path(file).is_file() and pid in Path(file).stem
    ]
    file_paths.extend(files)
    file_paths.extend(files_subfolders)

    # Empacotar os arquivos em um arquivo zip para facilitar o envio
    zip_file = f"Archives/PID {pid} {datetime.now(pytz.timezone('America/Manaus')).strftime('%d-%m-%Y-%H.%M')}.zip"
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in file_paths:
            arcname = os.path.relpath(file, os.path.join("exec", pid))
            zipf.write(file, arcname=arcname)

    return zip_file
