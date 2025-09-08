from dotenv import dotenv_values
from jpype import startJVM

environ = dotenv_values()

class_path: list[str] = environ.get("JPYPE_CLASSPATHS", [])

if class_path and isinstance(class_path, str):
    class_path = class_path.split(",") if "," in class_path else [class_path]


startJVM(classpath=class_path)
