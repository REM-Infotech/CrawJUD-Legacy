"""Defina e inicialize a aplicação Celery para processamento assíncrono de tarefas.

Este módulo importa a função make_celery do pacote crawjud.celery_app e
inicializa a instância global da aplicação Celery para uso em todo o projeto.

"""

from crawjud.celery_app import make_celery

app = make_celery()
