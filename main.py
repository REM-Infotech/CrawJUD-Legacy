from os import getcwd, path  # pragma: no cover
from pathlib import Path  # pragma: no cover

from clear import clear  # pragma: no cover
from dotenv import dotenv_values as values  # pragma: no cover

from app import create_app  # pragma: no cover

app, io = create_app()  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover

    clear()

    debug = values().get("DEBUG", "False").lower() in ("true")
    print(
        f"""
=======================================================

            Executando servidor Flask
            * Porta: {int(values().get("PORT", "8000"))}

=======================================================
              """
    )

    version_Path = Path(path.join(getcwd(), ".version"))
    if version_Path.exists() is False:
        from app.misc.checkout import checkout_release_tag

        with open(".version", "w") as f:
            f.write(checkout_release_tag())

    io.run(app, port=int(values().get("PORT", "8000")))
