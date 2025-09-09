# Documentação da Estrutura de Interfaces e Tipos

## Introdução

Este documento detalha a estrutura reorganizada dos tipos e interfaces do projeto CrawJUD, organizando-os de forma mais coesa e intuitiva por domínio de responsabilidade.

## Estrutura de Diretórios

### 📁 `core/` - Tipos Básicos e Fundamentais

Contém tipos primitivos, literais e customizados utilizados em toda a aplicação.

- **`primitives.py`**: Aliases de tipos básicos (DictData, ListData, PyNumbers, etc.)
- **`literals.py`**: Tipos literais para mensagens, status e enumerações
- **`custom.py`**: Tipos customizados com validação (StrProcessoCNJ, StrTime)

```python
from crawjud.interfaces.core import StrProcessoCNJ, DictData, StatusType
```

### 🔐 `auth/` - Tipos de Autenticação

Tipos relacionados à autenticação, sessão e credenciais.

- **`session.py`**: Tipos de sessão de usuário (CurrentUser, SessionDict)
- **`credentials.py`**: Tipos de credenciais de sistemas judiciais

```python
from crawjud.interfaces.auth import SessionDict, CredendialsDict
```

### 🤖 `bots/` - Tipos Relacionados aos Bots

Tipos específicos para configuração e operação dos bots.

- **`data.py`**: Estruturas de dados dos bots (BotData, DictReturnAuth)
- **`pje.py`**: Tipos específicos para bots do PJe
- **`projudi.py`**: Tipos específicos para bots do Projudi

```python
from crawjud.interfaces.bots import BotData, DictSeparaRegiao
```

### 🔧 `systems/` - Tipos de Sistemas Externos

Tipos relacionados a sistemas externos e suas integrações.

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
```

### ⚙️ `tasks/` - Tipos de Tarefas Assíncronas

Tipos relacionados ao processamento assíncrono e Celery.

- **`canvas.py`**: Tipos de Canvas (Signature, CeleryResult)
- **`task.py`**: Tipos de tarefas customizadas

```python
from crawjud.interfaces.tasks import Signature, Task
```

### 📋 `forms/` - Tipos de Formulários

Tipos para formulários dinâmicos dos bots.

- **`juridico.py`**: Formulários jurídicos
- **`administrativo.py`**: Formulários administrativos

```python
from crawjud.interfaces.forms import JuridicoFormFileAuth, FormDict
```

### 🎮 `controllers/` - Tipos de Controladores

Tipos relacionados aos controladores de sistema.

- **`file_service.py`**: Serviços de arquivos

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

## Benefícios da Nova Estrutura

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

## Migração de Código Existente

### Mapeamento de Imports Antigos para Novos

```python
# ANTES
from crawjud.interfaces.types import DictData, StrProcessoCNJ
from crawjud.interfaces.dict.bot import BotData
from crawjud.interfaces.pje import ProcessoJudicialDict
from crawjud.interfaces.session import SessionDict

# DEPOIS  
from crawjud.interfaces.core import DictData, StrProcessoCNJ
from crawjud.interfaces.bots import BotData
from crawjud.interfaces.systems.pje import ProcessoJudicialDict
from crawjud.interfaces.auth import SessionDict
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

## Considerações de Performance

- Imports organizados reduzem tempo de inicialização
- TYPE_CHECKING usado para imports apenas em tempo de verificação
- Re-exports controlados evitam imports desnecessários

## Versionamento e Compatibilidade

- Estrutura é retrocompatível via re-exports no `__init__.py` principal
- Deprecation warnings podem ser adicionados para imports antigos
- Migração gradual é possível mantendo ambas as estruturas temporariamente