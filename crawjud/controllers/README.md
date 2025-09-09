# Controllers - Controladores Principais

Este módulo contém os controladores principais da aplicação CrawJUD. Os controladores gerenciam a lógica de negócio, coordenam operações entre diferentes módulos e implementam workflows complexos.

## Arquitetura

### Padrão MVC
Os controladores seguem o padrão Model-View-Controller:
- **Model**: Interação com modelos de dados (SQLAlchemy)
- **View**: Processamento de requisições/respostas (API)
- **Controller**: Lógica de negócio e coordenação

### Responsabilidades
- Validação de dados de entrada
- Coordenação entre serviços
- Implementação de regras de negócio
- Gerenciamento de transações
- Tratamento de erros específicos

## Estrutura

### Main (`main/`)
Controladores principais do sistema:
- **BotController**: Gerenciamento de bots
- **UserController**: Gestão de usuários
- **ExecutionController**: Controle de execuções
- **AuthController**: Autenticação e autorização

## Controladores Principais

### BotController
```python
class BotController:
    """Controlador para operações de bots."""
    
    def __init__(self, db_session, logger):
        self.db = db_session
        self.logger = logger
    
    async def create_bot(self, bot_data: dict) -> dict:
        """Cria um novo bot no sistema."""
        # Validação
        await self._validate_bot_data(bot_data)
        
        # Criação
        bot = BotsCrawJUD(**bot_data)
        self.db.add(bot)
        await self.db.commit()
        
        return {"id": bot.id, "status": "created"}
    
    async def execute_bot(self, bot_id: int, user_id: int, params: dict) -> dict:
        """Executa um bot específico."""
        # Verificar permissões
        await self._check_bot_permissions(bot_id, user_id)
        
        # Iniciar execução
        execution = await self._start_execution(bot_id, user_id, params)
        
        # Enfileirar tarefa
        task = execute_bot_task.delay(execution.id)
        
        return {"execution_id": execution.id, "task_id": task.id}
```

### UserController
```python
class UserController:
    """Controlador para gestão de usuários."""
    
    async def authenticate_user(self, login: str, password: str) -> dict:
        """Autentica usuário no sistema."""
        user = await self._find_user_by_login(login)
        
        if not user or not self._verify_password(password, user.senha_hash):
            raise AuthenticationError("Credenciais inválidas")
        
        # Gerar token JWT
        token = self._generate_jwt_token(user)
        
        return {
            "user_id": user.id,
            "token": token,
            "expires_in": 3600
        }
    
    async def create_user(self, user_data: dict) -> dict:
        """Cria novo usuário."""
        # Validar dados
        await self._validate_user_data(user_data)
        
        # Verificar se já existe
        existing_user = await self._find_user_by_login(user_data['login'])
        if existing_user:
            raise ValidationError("Usuário já existe")
        
        # Criar usuário
        user = Users(**user_data)
        user.senha_hash = self._hash_password(user_data['password'])
        
        self.db.add(user)
        await self.db.commit()
        
        return {"id": user.id, "status": "created"}
```

### ExecutionController
```python
class ExecutionController:
    """Controlador para execuções de bots."""
    
    async def get_execution_status(self, execution_id: int) -> dict:
        """Obtém status de uma execução."""
        execution = await self._find_execution(execution_id)
        
        if not execution:
            raise NotFoundError("Execução não encontrada")
        
        return {
            "id": execution.id,
            "status": execution.status,
            "start_time": execution.start_time,
            "end_time": execution.end_time,
            "results": execution.results
        }
    
    async def cancel_execution(self, execution_id: int, user_id: int) -> dict:
        """Cancela uma execução em andamento."""
        execution = await self._find_execution(execution_id)
        
        # Verificar permissões
        if execution.user_id != user_id:
            raise PermissionError("Sem permissão para cancelar")
        
        # Cancelar tarefa Celery
        if execution.task_id:
            revoke(execution.task_id, terminate=True)
        
        # Atualizar status
        execution.status = "cancelled"
        execution.end_time = datetime.now()
        
        await self.db.commit()
        
        return {"status": "cancelled"}
```

### AuthController
```python
class AuthController:
    """Controlador para autenticação e autorização."""
    
    async def login(self, credentials: dict) -> dict:
        """Realiza login do usuário."""
        login = credentials.get('login')
        password = credentials.get('password')
        
        if not login or not password:
            raise ValidationError("Login e senha obrigatórios")
        
        user = await self._authenticate_user(login, password)
        
        # Criar sessão
        session_token = await self._create_session(user.id)
        
        # Gerar JWT
        jwt_token = self._generate_jwt(user)
        
        return {
            "access_token": jwt_token,
            "session_token": session_token,
            "user": {
                "id": user.id,
                "login": user.login,
                "email": user.email
            }
        }
    
    async def logout(self, user_id: int, session_token: str) -> dict:
        """Realiza logout do usuário."""
        # Invalidar sessão
        await self._invalidate_session(session_token)
        
        # Adicionar token à blacklist
        await self._blacklist_token(user_id)
        
        return {"status": "logged_out"}
    
    async def refresh_token(self, refresh_token: str) -> dict:
        """Renova token de acesso."""
        # Validar refresh token
        payload = self._validate_refresh_token(refresh_token)
        
        user_id = payload.get('user_id')
        user = await self._find_user_by_id(user_id)
        
        # Gerar novo token
        new_token = self._generate_jwt(user)
        
        return {"access_token": new_token}
```

## Padrões de Implementação

### Dependency Injection
```python
class BaseController:
    """Controlador base com dependências injetadas."""
    
    def __init__(self, db_session, logger, config):
        self.db = db_session
        self.logger = logger
        self.config = config
```

### Decoradores de Validação
```python
def validate_input(schema):
    """Decorador para validação de entrada."""
    def decorator(func):
        async def wrapper(self, data, *args, **kwargs):
            validated_data = schema.validate(data)
            return await func(self, validated_data, *args, **kwargs)
        return wrapper
    return decorator

class BotController:
    @validate_input(BotCreateSchema)
    async def create_bot(self, bot_data: dict):
        # Dados já validados
        pass
```

### Transaction Management
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def transaction(db_session):
    """Context manager para transações."""
    try:
        yield db_session
        await db_session.commit()
    except Exception:
        await db_session.rollback()
        raise

class UserController:
    async def create_user_with_license(self, user_data, license_data):
        async with transaction(self.db):
            user = Users(**user_data)
            self.db.add(user)
            
            license = LicensesUsers(**license_data)
            license.user = user
            self.db.add(license)
```

### Error Handling
```python
class ControllerError(Exception):
    """Exceção base para controladores."""
    pass

class ValidationError(ControllerError):
    """Erro de validação."""
    pass

class NotFoundError(ControllerError):
    """Recurso não encontrado."""
    pass

class PermissionError(ControllerError):
    """Erro de permissão."""
    pass
```

## Workflow Examples

### Execução de Bot Completa
```python
async def full_bot_execution_workflow(self, bot_id, user_id, params):
    """Workflow completo de execução de bot."""
    
    # 1. Validar permissões
    await self._validate_user_permissions(user_id, bot_id)
    
    # 2. Validar parâmetros
    validated_params = await self._validate_bot_params(bot_id, params)
    
    # 3. Criar execução
    execution = await self._create_execution(bot_id, user_id, validated_params)
    
    # 4. Obter credenciais
    credentials = await self._get_bot_credentials(bot_id, user_id)
    
    # 5. Enfileirar tarefa
    task = execute_bot_task.delay(execution.id, credentials)
    
    # 6. Atualizar execução com task_id
    execution.task_id = task.id
    await self.db.commit()
    
    # 7. Notificar via SocketIO
    await self._notify_execution_started(user_id, execution.id)
    
    return execution
```

### Processo de Autenticação
```python
async def authentication_workflow(self, login, password, ip_address):
    """Workflow completo de autenticação."""
    
    # 1. Rate limiting
    await self._check_rate_limit(ip_address)
    
    # 2. Validar credenciais
    user = await self._validate_credentials(login, password)
    
    # 3. Verificar se usuário está ativo
    if not user.active:
        raise AuthenticationError("Usuário inativo")
    
    # 4. Verificar licença
    await self._check_user_license(user.id)
    
    # 5. Criar sessão
    session = await self._create_user_session(user.id, ip_address)
    
    # 6. Gerar tokens
    access_token = self._generate_access_token(user)
    refresh_token = self._generate_refresh_token(user)
    
    # 7. Log de auditoria
    await self._log_authentication_event(user.id, ip_address, True)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "session_id": session.id
    }
```

## Testing

### Unit Tests
```python
import pytest
from unittest.mock import AsyncMock

class TestBotController:
    @pytest.fixture
    def controller(self):
        db_mock = AsyncMock()
        logger_mock = AsyncMock()
        return BotController(db_mock, logger_mock)
    
    async def test_create_bot_success(self, controller):
        bot_data = {"name": "Test Bot", "category": "judicial"}
        result = await controller.create_bot(bot_data)
        
        assert result["status"] == "created"
        controller.db.add.assert_called_once()
```

### Integration Tests
```python
async def test_full_bot_execution_workflow():
    """Teste de integração do workflow completo."""
    # Setup
    user = await create_test_user()
    bot = await create_test_bot()
    
    # Execute
    result = await controller.execute_bot(bot.id, user.id, {})
    
    # Assert
    assert result["execution_id"] is not None
    execution = await get_execution(result["execution_id"])
    assert execution.status == "pending"
```