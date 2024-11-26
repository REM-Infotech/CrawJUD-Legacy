from dotenv import dotenv_values as values
from app import create_app
from clear import clear

if __name__ == "__main__":

    clear()

    debug = values().get("DEBUG", "False").lower() in ("true")
    if not debug:
        with open(".version", "w") as f:
            from app.misc.checkout import checkout_release_tag

            version = checkout_release_tag()
            f.write(version)

        print(
            f"""
=======================================================

            Executando servidor Flask
            * Versão: {version}
            * Porta: 8000

=======================================================
              """
        )
    elif debug:
        print(
            """
=======================================================

            Executando servidor Flask
            * Porta: 8000

=======================================================
              """
        )

    app = create_app()
    from app import io

    io.run(app, port=values().get("PORT", "8000"))
