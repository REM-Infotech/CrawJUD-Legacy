"""CrawJUD - Sistema de Automação Jurídica.

Este é o módulo principal do CrawJUD, uma plataforma modular para automação de
rotinas jurídicas que integra robôs de automação, APIs web, tarefas assíncronas
e comunicação em tempo real.

Principais funcionalidades:
- Automação de sistemas judiciais brasileiros (PJe, ESAJ, Projudi, etc.)
- API web RESTful construída com Quart
- Sistema de tarefas assíncronas com Celery
- Banco de dados com SQLAlchemy
- Comunicação em tempo real via SocketIO
- Gerenciamento de credenciais e autenticação JWT

Exemplo de uso:
    >>> from crawjud.api import create_app
    >>> app = await create_app()
    >>> await app.run_task(host="0.0.0.0", port=8000)

Módulos principais:
    - api: Interface web RESTful
    - bots: Robôs de automação judicial
    - models: Modelos de banco de dados
    - tasks: Tarefas assíncronas Celery
    - utils: Utilitários e ferramentas auxiliares
"""
