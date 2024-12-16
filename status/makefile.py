import os
import pathlib
import zipfile
from datetime import datetime
from os import path
from pathlib import Path

import pytz


def makezip(pid: str) -> str:  # pragma: no cover

    file_paths = []
    exec_path = Path(path.join(pathlib.Path(__file__).cwd(), "exec", pid))
    files = [str(f) for f in exec_path.iterdir() if f.is_file()]
    files_subfolders = [
        path.join(f, file)
        for f in [str(f) for f in exec_path.iterdir() if f.is_dir()]
        for file in Path(f).iterdir()
        if Path(file).is_file()
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
