# API Routes - Endpoints da Aplicação

Este diretório contém todos os endpoints HTTP da API CrawJUD, organizados por funcionalidade. Cada módulo de rota implementa endpoints específicos para diferentes aspectos do sistema.

## Estrutura de Rotas

### Rotas de Autenticação (`auth.py`)

Gerencia autenticação e autorização de usuários:

- Login e logout
- Renovação de tokens JWT
- Validação de credenciais
- Gerenciamento de sessões

### Rotas de Bots (`bot/`)

Controla a execução e gerenciamento de robôs:

- Inicialização de bots (`/start_bot`)
- Status de execução
- Controle de processos
- Templates de execução

### Rotas de Configuração (`config/`)

Administração e configurações do sistema:

- Configurações administrativas
- Parâmetros de sistema
- Configurações de usuário
- Gerenciamento de licenças

### Rotas de Execução (`execution/`)

Controle e monitoramento de execuções:

- Histórico de execuções
- Status em tempo real
- Logs de execução
- Controle de filas

### Rotas de Dashboard (`dashboard.py`)

Interface administrativa e métricas:

- Painéis de controle
- Estatísticas de uso
- Métricas de performance
- Relatórios do sistema

### Rotas de Credenciais (`credentials.py`)

Gerenciamento de credenciais e acessos:

- Configuração de credenciais
- Validação de acessos
- Gerenciamento de tokens
- Configurações de segurança

## Padrões de Implementação

### Decoradores

Todas as rotas utilizam decoradores padronizados:

```python
@blueprint.route("/endpoint", methods=["GET", "POST"])
@CrossDomain(origin="*", methods=["GET", "POST"])
@jwt_required
async def endpoint():
    # Implementação
```

### Tratamento de Erros

- Captura centralizada de exceções
- Logging estruturado de erros
- Respostas padronizadas de erro
- Códigos de status HTTP apropriados

### Validação

- Validação de dados de entrada
- Sanitização de parâmetros
- Verificação de permissões
- Validação de tokens JWT

### Resposta Padronizada

```python
return await make_response(
    jsonify(message="Sucesso", data=result),
    200
)
```

## Configuração de CORS

Todas as rotas são configuradas com:

- Origens permitidas: `*` (desenvolvimento)
- Métodos: `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`
- Headers personalizados permitidos
- Credenciais habilitadas

## Middleware

### Autenticação JWT

- Verificação automática de tokens
- Renovação de tokens expirados
- Controle de acesso baseado em roles

### Logging

- Log estruturado de todas as requisições
- Rastreamento de erros
- Métricas de performance

## Uso

```python
from crawjud.api.routes.bot import bot
from crawjud.api.routes.auth import auth

# Registrar blueprints
app.register_blueprint(bot)
app.register_blueprint(auth)
```
