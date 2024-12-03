from os import getcwd, path
from pathlib import Path

from clear import clear
from dotenv import dotenv_values as values

from app import create_app

app, io = create_app()


if __name__ == "__main__":

    clear()

    debug = values().get("DEBUG", "False").lower() in ("true")
    print(
        """
=======================================================

            Executando servidor Flask
            * Porta: 8000

=======================================================
              """
    )

    version_Path = Path(path.join(getcwd(), ".version"))
    if version_Path.exists() is False:
        from app.misc.checkout import checkout_release_tag

        with open(".version", "w") as f:
            f.write(checkout_release_tag())

    io.run(app, port=int(values().get("PORT", "8000")))
