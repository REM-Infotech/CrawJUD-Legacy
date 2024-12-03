import pathlib
import os


def test_path():

    pathlibing = pathlib.Path(__file__).cwd()
    print(os.path.join(pathlibing))


test_path()
