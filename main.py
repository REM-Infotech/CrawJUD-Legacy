from importlib import import_module
from app import create_app
from clear import clear
checkout = import_module("app.misc.checkout", __name__)

if __name__ == "__main__":
    print("Iniciando monitoramento de mudanças e servidor Flask...")
    clear()
    with open(".version", "w") as f:
        version = checkout.checkout_release_tag()
        f.write(version)

    app = create_app()
    from app import io
    io.run(app, port=8000)
