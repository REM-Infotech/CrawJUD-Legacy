# CrawJUD - Módulo Principal

Este é o módulo principal do CrawJUD, uma plataforma modular para automação de rotinas jurídicas. O sistema integra robôs de automação, APIs web, tarefas assíncronas e comunicação em tempo real.

## Arquitetura

O CrawJUD é construído sobre uma arquitetura moderna e escalável utilizando:

- **Quart**: Framework web assíncrono (baseado em Flask)
- **SQLAlchemy**: ORM para gerenciamento de banco de dados
- **Celery**: Sistema de filas para tarefas assíncronas
- **Redis**: Cache e broker para filas de tarefas
- **Selenium**: Automação de navegadores web
- **SocketIO**: Comunicação em tempo real

## Estrutura de Diretórios

### Módulos Principais

- [`api/`](./api/README.md) - API web RESTful com Quart
- [`bots/`](./bots/README.md) - Robôs de automação para sistemas judiciais
- [`models/`](./models/README.md) - Modelos de banco de dados SQLAlchemy
- [`tasks/`](./tasks/README.md) - Tarefas assíncronas do Celery
- [`utils/`](./utils/README.md) - Utilitários e ferramentas auxiliares

### Módulos de Suporte

- [`common/`](./common/README.md) - Exceções e utilitários comuns
- [`controllers/`](./controllers/README.md) - Controladores principais da aplicação
- [`decorators/`](./decorators/README.md) - Decoradores Python customizados
- [`interfaces/`](./interfaces/README.md) - Interfaces de tipos e protocolos
- [`resources/`](./resources/README.md) - Recursos estáticos e elementos
- [`custom/`](./custom/README.md) - Funcionalidades customizadas

## Fluxo de Operação

1. **Inicialização**: A aplicação Quart é configurada e inicializada
2. **Autenticação**: Usuários se autenticam via JWT
3. **Solicitação de Bot**: Clientes solicitam execução de bots via API
4. **Processamento Assíncrono**: Tarefas são enfileiradas no Celery
5. **Execução**: Bots são executados com automação Selenium
6. **Notificação**: Resultados são enviados via SocketIO

## Configuração

A aplicação é configurada através de:
- `quartconf.py` - Configurações do Quart
- `celery_app.py` - Configurações do Celery
- Variáveis de ambiente (`.env`)

## Desenvolvimento

Para contribuir com o projeto, consulte:
- [Guia de Contribuição](../docs/CONTRIBUTING.md)
- [Estrutura do Projeto](../PROJECT-STRUCTURE.md)
- [Política de Segurança](../docs/SECURITY.md)
