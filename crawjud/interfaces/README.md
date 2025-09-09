# Interfaces - Definições de Tipos e Protocolos

Este módulo contém as definições de interfaces, protocolos, tipos customizados e contratos da aplicação CrawJUD. As interfaces garantem consistência de tipos e facilitam a manutenção do código através de definições claras de contratos.

## Arquitetura

### Type Hints e Protocols
Utilização de Python typing para:
- Definição de contratos claros
- Verificação estática de tipos
- Documentação de APIs
- IntelliSense melhorado

### Estrutura Organizacional
As interfaces são organizadas por domínio de responsabilidade:

## Estrutura de Diretórios

### 📁 `core/` - Tipos Básicos e Fundamentais

Contém tipos primitivos, literais e customizados utilizados em toda a aplicação:

- **`primitives.py`**: Aliases de tipos básicos (DictData, ListData, PyNumbers, etc.)
- **`literals.py`**: Tipos literais para mensagens, status e enumerações
- **`custom.py`**: Tipos customizados com validação (StrProcessoCNJ, StrTime)

```python
from crawjud.interfaces.core import StrProcessoCNJ, DictData, StatusType
```

### 🔐 `auth/` - Tipos de Autenticação

Tipos relacionados à autenticação, sessão e credenciais:

- **`session.py`**: Tipos de sessão de usuário (CurrentUser, SessionDict)
- **`credentials.py`**: Tipos de credenciais de sistemas judiciais

```python
from crawjud.interfaces.auth import SessionDict, CredendialsDict

class AuthProvider(Protocol):
    """Interface para provedores de autenticação."""
    
    async def authenticate(self, credentials: dict) -> dict:
        """Autentica usuário com credenciais."""
        ...
    
    async def refresh_token(self, refresh_token: str) -> dict:
        """Renova token de acesso."""
        ...
```

### 🤖 `bots/` - Tipos Relacionados aos Bots

Tipos específicos para configuração e operação dos bots:

- **`data.py`**: Estruturas de dados dos bots (BotData, DictReturnAuth)
- **`pje.py`**: Tipos específicos para bots do PJe
- **`projudi.py`**: Tipos específicos para bots do Projudi

```python
from crawjud.interfaces.bots import BotData, DictSeparaRegiao

class BotInterface(Protocol):
    """Interface base para todos os bots."""
    
    async def initialize(self) -> None:
        """Inicializa o bot."""
        ...
    
    async def authenticate(self, credentials: dict) -> bool:
        """Autentica no sistema judicial."""
        ...
    
    async def execute_task(self, task_data: dict) -> dict:
        """Executa tarefa específica."""
        ...
    
    async def cleanup(self) -> None:
        """Finaliza recursos do bot."""
        ...
```

### 🔧 `systems/` - Tipos de Sistemas Externos

Tipos relacionados a sistemas externos e suas integrações:

#### `systems/pje/` - Sistema PJe
- **`processos.py`**: Tipos principais de processos judiciais
- **`partes.py`**: Tipos de partes processuais
- **`audiencias.py`**: Tipos de audiências
- **`assuntos.py`**: Tipos de assuntos processuais

#### `systems/webdriver/` - WebDriver
- **`config.py`**: Configurações de WebDriver (Chrome, Firefox)

```python
from crawjud.interfaces.systems.pje import ProcessoJudicialDict
from crawjud.interfaces.systems.webdriver import ChromeConfig

class PJeInterface(Protocol):
    """Interface para operações do PJe."""
    
    async def get_process_capa(self, process_number: str) -> dict:
        """Obtém capa processual."""
        ...
    
    async def get_process_pauta(self, date_range: tuple) -> List[dict]:
        """Obtém pauta de processos."""
        ...
```

### ⚙️ `tasks/` - Tipos de Tarefas Assíncronas

Tipos relacionados ao processamento assíncrono e Celery:

- **`canvas.py`**: Tipos de Canvas (Signature, CeleryResult)
- **`task.py`**: Tipos de tarefas customizadas

```python
from crawjud.interfaces.tasks import Signature, Task

class CeleryTask(Protocol):
    """Interface para tarefas Celery."""
    
    def delay(self, *args, **kwargs) -> AsyncResult:
        """Executa tarefa assincronamente."""
        ...
    
    def apply_async(self, args=None, kwargs=None, **options) -> AsyncResult:
        """Executa com opções customizadas."""
        ...
```

### 📋 `forms/` - Tipos de Formulários

Tipos para formulários dinâmicos dos bots:

- **`juridico.py`**: Formulários jurídicos
- **`administrativo.py`**: Formulários administrativos

```python
from crawjud.interfaces.forms import JuridicoFormFileAuth, FormDict

class FormValidator(Protocol):
    """Interface para validação de formulários."""
    
    def validate(self, data: dict) -> tuple[bool, dict]:
        """Valida dados do formulário."""
        ...
```

### 🎮 `controllers/` - Tipos de Controladores

Tipos relacionados aos controladores de sistema:

- **`file_service.py`**: Serviços de arquivos

```python
from typing import Protocol, Generic, TypeVar

T = TypeVar('T')

class Repository(Protocol, Generic[T]):
    """Interface genérica para repositórios."""
    
    async def create(self, entity: T) -> T:
        """Cria nova entidade."""
        ...
    
    async def get_by_id(self, entity_id: int) -> Optional[T]:
        """Busca entidade por ID."""
        ...
```

## Uso e Importações

### Importação por Domínio

```python
# Importar módulo completo
from crawjud.interfaces import core, auth, bots, systems

# Usar tipos específicos
user_session: auth.SessionDict = {...}
bot_data: bots.BotData = {...}
processo: systems.pje.ProcessoJudicialDict = {...}
```

### Importação Direta de Tipos

```python
# Tipos básicos
from crawjud.interfaces.core import DictData, StrProcessoCNJ, StatusType

# Tipos de autenticação
from crawjud.interfaces.auth import SessionDict, CurrentUser

# Tipos de bots
from crawjud.interfaces.bots import BotData, DictReturnAuth

# Tipos de sistemas
from crawjud.interfaces.systems.pje import ProcessoJudicialDict, PartesProcessoPJeDict
from crawjud.interfaces.systems.webdriver import ChromeConfig, FirefoxConfig
```

## Benefícios da Estrutura

### 🎯 **Organização por Domínio**
- Tipos relacionados ficam agrupados
- Facilita localização e manutenção
- Reduz acoplamento entre módulos

### 📚 **Clareza de Responsabilidades**
- Cada diretório tem responsabilidade bem definida
- Nomenclatura consistente e intuitiva
- Documentação organizada por contexto

### 🔄 **Facilidade de Manutenção**
- Mudanças em um domínio não afetam outros
- Imports mais claros e organizados
- Redução de dependências circulares

### 🚀 **Escalabilidade**
- Estrutura preparada para novos tipos e sistemas
- Padrão consistente para extensões
- Modularidade que facilita testes unitários

## Validação de Interfaces

### Runtime Type Checking
```python
from typing import runtime_checkable

@runtime_checkable
class Serializable(Protocol):
    """Interface para objetos serializáveis."""
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        ...

def serialize_if_possible(obj: Any) -> Optional[dict]:
    """Serializa objeto se implementar interface."""
    if isinstance(obj, Serializable):
        return obj.to_dict()
    return None
```

### Type Guards
```python
from typing import TypeGuard

def is_valid_user_dict(data: dict) -> TypeGuard[UserDict]:
    """Verifica se dicionário é UserDict válido."""
    required_keys = {'id', 'login', 'email', 'nome_usuario', 'active'}
    return all(key in data for key in required_keys)
```

## Convenções de Nomenclatura

- **Arquivos**: snake_case (ex: `primitives.py`, `file_service.py`)
- **Diretórios**: snake_case (ex: `auth/`, `systems/pje/`)
- **Tipos**: PascalCase (ex: `ProcessoJudicialDict`, `BotData`)
- **Type aliases**: PascalCase (ex: `DictData`, `ListType`)

## Documentação de Tipos

Cada arquivo de tipo deve incluir:

1. **Docstring do módulo** explicando o propósito
2. **Documentação de cada tipo** com Args e Returns
3. **Exemplos de uso** quando apropriado
4. **Lista `__all__`** com exports explícitos