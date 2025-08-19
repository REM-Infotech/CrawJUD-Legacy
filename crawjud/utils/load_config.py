"""Configuration loader module.

Provides functionality to load configuration from an object.
"""

from __future__ import annotations

from os import environ
from typing import AnyStr, Self, TypedDict

from dotenv import load_dotenv

load_dotenv()

config_dict_model = {
    "broker_url": "",
    "result_backend": "",
    "task_ignore_result": True,
    "broker_connection_retry_on_startup": True,
    "timezone": "",
    "task_create_missing_queues": True,
}


class CeleryConfig(TypedDict):
    """Defina o modelo de configuração para o celery com campos obrigatórios.

    Args:
        broker_url (str): URL do broker para o celery.
        result_backend (str): Backend de resultados do celery.
        task_ignore_result (bool): Ignora o resultado das tarefas.
        broker_connection_retry_on_startup (bool): Tenta reconectar ao broker na inicialização.
        timezone (str): Fuso horário utilizado pelo celery.
        task_create_missing_queues (bool): Cria filas ausentes automaticamente.

    Returns:
        TypedDict: Dicionário tipado representando a configuração do celery.

    """

    broker_url: str
    result_backend: str
    task_ignore_result: bool
    broker_connection_retry_on_startup: bool
    timezone: str
    task_create_missing_queues: bool


class Config:
    """Class config para o celery app."""

    celery_config: CeleryConfig
    broker_url: str
    result_backend: str
    task_ignore_result: bool
    task_create_missing_queues: bool
    broker_connection_retry_on_startup: bool
    timezone: str

    @classmethod
    def load_config(cls, **kwrgs: AnyStr) -> Self:
        """Carregue a configuração do celery a partir dos argumentos fornecidos.

        Args:
            **kwrgs (str): Argumentos de configuração para o celery.

        Returns:
            Self: Instância da classe Config inicializada com os argumentos.

        """
        return cls(**kwrgs)

    def convert_bool(self, v: str) -> bool:
        return v.lower() == "true" or v == 1

    def __init__(self, **kwargs: AnyStr) -> None:
        """Inicializa a configuração do celery a partir dos argumentos fornecidos.

        Args:
            **kwargs (str): Argumentos de configuração para o celery.



        """
        arguments = kwargs.copy()
        arguments.update(environ)
        self.celery_config = CeleryConfig(**{
            k.lower(): v
            for k, v in arguments.items()
            if k.lower() in CeleryConfig.__annotations__
        })

        for k, v in self.celery_config.items():
            if v.lower() == "true":
                v = True

            setattr(self, k, v)
