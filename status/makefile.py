import os
import zipfile
from datetime import datetime

import pytz


def makezip(pid: str) -> str:

    file_paths = []
    temp_path = os.path.join(os.getcwd(), "Temp", pid)
    for root, dirs, files in os.walk(temp_path):
        for file in files:

            if pid in file:

                if ".json" in file:
                    continue

                other_folder = root.split(pid)

                if len(other_folder) > 1:

                    barra = "\\" if "\\" in other_folder[1] else "/"
                    other_folder = other_folder[1].replace(barra, "")
                    file_path = os.path.join("Temp", pid, other_folder, file)
                    file_paths.append(file_path)

                elif len(other_folder) == 1:
                    file_path = os.path.join("Temp", pid, file)
                    file_paths.append(file_path)

    # Empacotar os arquivos em um arquivo zip para facilitar o envio
    zip_file = f"Archives/PID {pid} {datetime.now(pytz.timezone('America/Manaus')).strftime('%d-%m-%Y-%H.%M')}.zip"
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in file_paths:
            zipf.write(file)

    return zip_file
