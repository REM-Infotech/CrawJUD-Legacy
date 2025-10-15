# Models - Modelos de Banco de Dados

Este módulo contém todos os modelos de banco de dados do CrawJUD, implementados com SQLAlchemy. Os modelos definem a estrutura de dados, relacionamentos e operações de persistência do sistema.

## Arquitetura

### ORM SQLAlchemy

- Modelos declarativos
- Relacionamentos automáticos
- Migrações de schema
- Queries otimizadas

### Estrutura de Dados

Os modelos são organizados por domínio:

- **Usuários e Autenticação**
- **Bots e Execuções**
- **Agendamento e Cron**
- **Licenças e Clientes**

## Modelos Principais

### Usuários (`users.py`)

#### Users

```python
class Users:
    id: int
    login: str
    email: str
    nome_usuario: str
    senha_hash: str
    created_at: datetime
    updated_at: datetime
```

#### SuperUser

```python
class SuperUser:
    id: int
    user_id: int
    permissions: list
    created_at: datetime
```

#### LicensesUsers

```python
class LicensesUsers:
    id: int
    name_client: str
    cpf_cnpj: str
    license_token: str
    active: bool
    created_at: datetime
```

### Bots (`bots.py`)

#### BotsCrawJUD

```python
class BotsCrawJUD:
    id: int
    display_name: str
    bot_name: str
    description: str
    category: str
    active: bool
    parameters: dict
    created_at: datetime
```

#### Executions

```python
class Executions:
    id: int
    bot_id: int
    user_id: int
    status: str
    start_time: datetime
    end_time: datetime
    results: dict
    error_log: str
```

#### ThreadBots

```python
class ThreadBots:
    id: int
    execution_id: int
    thread_id: str
    pid: int
    status: str
    created_at: datetime
```

#### Credentials

```python
class Credentials:
    id: int
    user_id: int
    bot_id: int
    username: str
    password_encrypted: str
    additional_data: dict
    created_at: datetime
```

### Agendamento (`schedule.py`)

#### ScheduleModel

```python
class ScheduleModel:
    id: int
    name: str
    bot_id: int
    user_id: int
    crontab_id: int
    enabled: bool
    last_run: datetime
    next_run: datetime
```

#### CrontabModel

```python
class CrontabModel:
    id: int
    minute: str
    hour: str
    day_of_week: str
    day_of_month: str
    month_of_year: str
    timezone: str
```

### Relacionamentos Secundários (`secondaries.py`)

#### admins

Tabela de relacionamento para administradores:

```python
admins = Table(
    'admins',
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('license_id', Integer, ForeignKey('licenses_users.id'))
)
```

#### execution_bots

Tabela de relacionamento para execuções e bots:

```python
execution_bots = Table(
    'execution_bots',
    Column('execution_id', Integer, ForeignKey('executions.id')),
    Column('bot_id', Integer, ForeignKey('bots_crawjud.id'))
)
```

## Relacionamentos

### One-to-Many

- Users → Executions
- Users → Credentials
- BotsCrawJUD → Executions
- ScheduleModel → Executions

### Many-to-Many

- Users ↔ LicensesUsers (através de admins)
- Executions ↔ BotsCrawJUD (através de execution_bots)

### One-to-One

- ScheduleModel → CrontabModel
- ThreadBots → Executions

## Inicialização do Banco

### Função `init_database()`

A função principal de inicialização:

1. **Criação de Tabelas**: `db.create_all()`
2. **Usuário Root**: Criação do usuário administrador
3. **Licença Inicial**: Configuração da licença principal
4. **Bots Padrão**: Importação de bots do `export.json`
5. **Commit**: Persistência das mudanças

### Dados Iniciais

Os dados iniciais são carregados de:

- Variáveis de ambiente (usuário root)
- Arquivo `export.json` (bots disponíveis)
- Configurações padrão do sistema

## Validações

### Modelos

- Validação de tipos
- Constraints de banco
- Validações customizadas
- Sanitização de dados

### Segurança

- Hash de senhas (bcrypt)
- Criptografia de credenciais
- Tokens seguros
- Validação de inputs

## Queries Comuns

### Usuários

```python
# Buscar usuário por login
user = Users.query.filter(Users.login == username).first()

# Usuários ativos com licenças
active_users = Users.query.join(LicensesUsers).filter(
    LicensesUsers.active == True
).all()
```

### Execuções

```python
# Execuções recentes
recent_executions = Executions.query.filter(
    Executions.start_time >= datetime.now() - timedelta(days=7)
).order_by(Executions.start_time.desc()).all()

# Execuções por status
running_executions = Executions.query.filter(
    Executions.status == 'running'
).all()
```

### Bots

```python
# Bots ativos
active_bots = BotsCrawJUD.query.filter(
    BotsCrawJUD.active == True
).all()

# Bots por categoria
judicial_bots = BotsCrawJUD.query.filter(
    BotsCrawJUD.category == 'judicial'
).all()
```

## Migrações

### Versionamento

- Controle de versão do schema
- Migrações incrementais
- Rollback seguro
- Backup automático

### Estratégias

- Migrações online (sem downtime)
- Validação de dados
- Testes de migração
- Monitoramento de performance

## Performance

### Otimizações

- Índices apropriados
- Queries otimizadas
- Lazy loading
- Connection pooling

### Monitoramento

- Slow query log
- Métricas de performance
- Análise de queries
- Otimização contínua
