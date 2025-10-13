import asyncio

from termcolor import colored
from tqdm import tqdm

from app import app


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
