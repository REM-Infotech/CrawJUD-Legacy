from dotenv import dotenv_values
from app import create_app
from clear import clear

if __name__ == "__main__":

    clear()

    debug = dotenv_values().get("DEBUG", "False").lower() in ("true")
    if not debug:
        with open(".version", "w") as f:
            from app.misc.checkout import checkout_release_tag

            version = checkout_release_tag()
            f.write(version)

        print("=======================================================\n")
        print("Executando servidor Flask")
        print(f" * Versão: {version}")
        print(" * Porta: 8000")
        print("\n=======================================================")

    elif debug:
        print("=======================================================\n")
        print("Executando servidor Flask")
        print(" * Porta: 8000")
        print("\n=======================================================")

    app = create_app()
    from app import io

    io.run(app, port=8000)
