# Documentação da Estrutura do App

Este documento detalha a estrutura e os componentes do diretório `app` no projeto CrawJUD-Bots.

## Componentes Principais

### `__init__.py`
Contém a classe `AppFactory` responsável por:
- Inicialização da aplicação
- Carregamento de configurações
- Gerenciamento de inicialização do servidor
- Registro de extensões e rotas

### `asgi.py`
Ponto de entrada da aplicação ASGI que:
- Define variáveis de ambiente para produção
- Inicializa a aplicação Quart
- Serve como arquivo principal de inicialização do servidor

### `beat.py`
Agendador Celery beat que:
- Gerencia tarefas periódicas
- Configura logging para jobs agendados
- Utiliza um agendador personalizado baseado em banco de dados

### `worker.py`
Implementação do worker Celery que:
- Processa tarefas
- Gerencia configurações de concorrência
- Configura logging do worker

## Diretório Core (`core/`)

### `configurator.py`
Módulo de gerenciamento de configuração que:
- Carrega configurações específicas do ambiente
- Inicializa extensões da aplicação
- Configura logging e conexões com banco de dados

### `extensions.py`
Módulo de inicialização de extensões que:
- Configura Flask-Mail
- Configura segurança Talisman
- Inicializa SQLAlchemy
- Configura outras extensões Flask/Quart

### `routing.py`
Módulo de registro de rotas que:
- Registra endpoints da API
- Configura rotas WebSocket
- Gerencia padrões de URL

## Diretório Models (`models/`)
Contém modelos SQLAlchemy para:
- Gerenciamento de usuários
- Agendamento de tarefas
- Configuração do sistema
- Persistência de dados

## Diretório Routes (`routes/`)
Contém manipuladores de rota para:
- Endpoints da API
- Conexões WebSocket
- Operações do sistema
- Gerenciamento de tarefas

## Diretório Forms (`Forms/`)
Contém validadores e processadores de formulários para:
- Validação de entrada de dados
- Processamento de requisições
- Renderização de formulários

## Configuração de Ambiente
A aplicação suporta múltiplos ambientes:
- Desenvolvimento
- Produção
- Teste

Cada ambiente possui sua classe de configuração específica em `config.py`.
