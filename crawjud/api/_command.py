import asyncio

from clear import clear
from termcolor import colored
from tqdm import tqdm

from crawjud.api import app, main_app


@app.cli.command()
def init_database() -> None:
    """Inicializa o banco de dados criando todas as tabelas necessárias."""
    from crawjud.models import init_database

    asyncio.run(init_database())

    tqdm.write(
        colored(
            "Banco de dados inicializado com sucesso!",
            color="green",
            attrs=["bold", "blink"],
        ),
    )


@app.cli.command()
def start() -> None:
    """Executa o App."""
    try:
        clear()
        asyncio.run(main_app())
    except KeyboardInterrupt:
        from blessed import Terminal

        term = Terminal()

        tqdm.write(term.home + term.clear + term.move_y(term.height // 2))
        tqdm.write(
            term.black_on_darkkhaki(term.center("press any key to continue.")),
        )

        with term.cbreak(), term.hidden_cursor():
            term.inkey()

        clear()
