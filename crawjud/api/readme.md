# API - Interface Web RESTful

O módulo API fornece uma interface web RESTful construída com Quart (framework assíncrono baseado em Flask). Este módulo gerencia toda a comunicação HTTP entre clientes e o sistema CrawJUD.

## Arquitetura

A API é organizada em camadas:

- **Rotas**: Endpoints HTTP organizados por funcionalidade
- **Namespaces**: Agrupamento lógico de rotas relacionadas
- **Middlewares**: Processamento de requisições e respostas
- **Autenticação**: Sistema JWT para controle de acesso

## Estrutura

### Diretórios

- [`routes/`](./routes/README.md) - Endpoints da API organizados por funcionalidade
- [`namespaces/`](./namespaces/README.md) - Agrupamentos de rotas relacionadas

### Arquivos Principais

- `__init__.py` - Configuração e inicialização da aplicação Quart
- `quartconf.py` - Configurações específicas do Quart

## Recursos da API

### Autenticação
- Sistema JWT (JSON Web Tokens)
- Middleware de autenticação
- Controle de sessões com Redis

### CORS
- Configuração de Cross-Origin Resource Sharing
- Suporte a origens múltiplas
- Headers personalizados permitidos

### Middleware
- Proxy headers para deployment
- Tratamento de erros centralizado
- Logging de requisições

## Endpoints Principais

### Autenticação (`/auth`)
- Login e logout de usuários
- Renovação de tokens JWT
- Gerenciamento de sessões

### Bots (`/bot`)
- Inicialização de robôs
- Monitoramento de execuções
- Controle de status

### Configuração (`/config`)
- Configurações administrativas
- Gerenciamento de parâmetros
- Configurações de sistema

### Execução (`/execution`)
- Controle de execuções de bots
- Histórico de execuções
- Status e logs

### Dashboard (`/dashboard`)
- Métricas do sistema
- Painéis administrativos
- Estatísticas de uso

### Credenciais (`/credentials`)
- Gerenciamento de credenciais
- Configurações de acesso
- Validação de credenciais

## Uso

```python
from crawjud.api import create_app

# Criar aplicação
app = await create_app()

# Executar aplicação
await app.run_task(host="0.0.0.0", port=8000)
```

## Configuração

A API é configurada através de:
- Variáveis de ambiente
- Arquivo `quartconf.py`
- Configurações de database
- Configurações de JWT

## Extensões

- **SQLAlchemy**: ORM para banco de dados
- **JWT Extended**: Autenticação JWT
- **CORS**: Cross-Origin Resource Sharing
- **SocketIO**: Comunicação em tempo real
- **Session**: Gerenciamento de sessões
- **Mail**: Envio de emails