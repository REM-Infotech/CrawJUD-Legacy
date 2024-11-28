import os
import shutil

import psutil
from psutil import Process


def DelCache(pid=None):

    for root, dirs, files in os.walk(os.path.join(os.getcwd())):

        if pid in root:

            try:
                shutil.rmtree(root)

            except PermissionError as e:
                print(e)
                stop_exec(find_open_files(root))
                shutil.rmtree(root)


def find_open_files(filename):
    """
    Finds processes that have the specified file open.

    ## Args:
        * filename (str): The path to the file.

    ## Returns:
        * list: A list of `psutil.Process` objects that have the file open.
    """
    open_files = []
    get_process = psutil.process_iter(["cmdline"])

    for proc in get_process:

        try:
            listfile = proc.open_files()
            for pathfile in listfile:

                if filename in pathfile.path:
                    open_files.append(proc)

        except psutil.AccessDenied:
            pass

    return open_files


def stop_exec(to_stop):

    for process in to_stop:
        try:
            Process.kill(process)

        except psutil.NoSuchProcess:
            continue
