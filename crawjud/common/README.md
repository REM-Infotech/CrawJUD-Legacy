# Common - Exceções e Utilitários Comuns

Este módulo contém exceções personalizadas e utilitários comuns utilizados em todo o sistema CrawJUD. As funcionalidades são organizadas para fornecer tratamento de erros consistente e funcionalidades compartilhadas.

## Estrutura

### Exceções (`exceptions/`)

Sistema de exceções customizadas organizadas por categoria:

- **Database**: Exceções relacionadas ao banco de dados
- **Bot**: Exceções específicas de bots de automação
- **Mail**: Exceções de envio de email
- **Validação**: Exceções de validação de dados
- **E-law**: Exceções específicas do sistema E-law
- **Selenium WebDriver**: Exceções de automação web
- **Form**: Exceções de formulários

## Exceções Personalizadas

### Exceções de Database (`database.py`)

```python
class DatabaseConnectionError(Exception):
    """Erro de conexão com banco de dados."""
    pass

class DatabaseQueryError(Exception):
    """Erro na execução de query."""
    pass

class DatabaseIntegrityError(Exception):
    """Erro de integridade referencial."""
    pass
```

### Exceções de Bot (`bot/`)

Exceções específicas para diferentes sistemas:

#### ProJudi (`bot/projudi.py`)

```python
class ProJudiAuthenticationError(Exception):
    """Erro de autenticação no ProJudi."""
    pass

class ProJudiNavigationError(Exception):
    """Erro de navegação no ProJudi."""
    pass

class ProJudiDataExtractionError(Exception):
    """Erro na extração de dados do ProJudi."""
    pass
```

### Exceções de Mail (`mail.py`)

```python
class EmailConfigurationError(Exception):
    """Erro de configuração de email."""
    pass

class EmailSendError(Exception):
    """Erro no envio de email."""
    pass

class EmailTemplateError(Exception):
    """Erro no template de email."""
    pass
```

### Exceções de Validação (`validacao.py`)

```python
class ValidationError(Exception):
    """Erro de validação de dados."""
    pass

class CPFValidationError(ValidationError):
    """Erro de validação de CPF."""
    pass

class CNPJValidationError(ValidationError):
    """Erro de validação de CNPJ."""
    pass

class EmailValidationError(ValidationError):
    """Erro de validação de email."""
    pass
```

### Exceções E-law (`elaw.py`)

```python
class ElawConnectionError(Exception):
    """Erro de conexão com E-law."""
    pass

class ElawAuthenticationError(Exception):
    """Erro de autenticação no E-law."""
    pass

class ElawAPIError(Exception):
    """Erro na API do E-law."""
    pass
```

### Exceções Selenium (`selenium_webdriver.py`)

```python
class WebDriverInitializationError(Exception):
    """Erro na inicialização do WebDriver."""
    pass

class ElementNotFoundError(Exception):
    """Elemento não encontrado na página."""
    pass

class PageLoadTimeoutError(Exception):
    """Timeout no carregamento da página."""
    pass

class CaptchaError(Exception):
    """Erro relacionado a captcha."""
    pass
```

### Exceções de Form (`_form.py`)

```python
class FormValidationError(Exception):
    """Erro de validação de formulário."""
    pass

class FormSubmissionError(Exception):
    """Erro no envio de formulário."""
    pass

class FormFieldError(Exception):
    """Erro em campo específico do formulário."""
    pass
```

## Padrões de Uso

### Hierarquia de Exceções

```python
class CrawJUDError(Exception):
    """Exceção base do CrawJUD."""
    pass

class BotError(CrawJUDError):
    """Exceção base para bots."""
    pass

class PJeError(BotError):
    """Exceção específica do PJe."""
    pass
```

### Informações Contextuais

```python
class DetailedError(Exception):
    """Exceção com informações detalhadas."""

    def __init__(self, message, error_code=None, context=None):
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = datetime.now()
```

### Logging Automático

```python
class LoggedError(Exception):
    """Exceção que faz log automático."""

    def __init__(self, message, logger=None):
        super().__init__(message)
        if logger:
            logger.error(f"Error occurred: {message}")
```

## Tratamento de Erros

### Try-Catch Padronizado

```python
try:
    # Operação que pode falhar
    result = risky_operation()
except DatabaseConnectionError as e:
    # Tratamento específico para DB
    logger.error(f"Database error: {e}")
    raise
except ValidationError as e:
    # Tratamento para validação
    return {"error": "Invalid data", "details": str(e)}
except Exception as e:
    # Fallback genérico
    logger.exception("Unexpected error")
    raise CrawJUDError("Internal error") from e
```

### Decorador para Tratamento

```python
def handle_errors(error_map=None):
    """Decorador para tratamento automático de erros."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if error_map and type(e) in error_map:
                    raise error_map[type(e)](str(e)) from e
                raise
        return wrapper
    return decorator
```

## Utilitários Comuns

### Validadores

```python
def validate_cpf(cpf: str) -> bool:
    """Valida CPF brasileiro."""
    if not cpf or not cpf.isdigit() or len(cpf) != 11:
        raise CPFValidationError("CPF inválido")
    # Lógica de validação
    return True

def validate_email(email: str) -> bool:
    """Valida formato de email."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise EmailValidationError("Email inválido")
    return True
```

### Formatadores

```python
def format_cpf(cpf: str) -> str:
    """Formata CPF com pontuação."""
    clean_cpf = re.sub(r'\D', '', cpf)
    return f"{clean_cpf[:3]}.{clean_cpf[3:6]}.{clean_cpf[6:9]}-{clean_cpf[9:]}"

def format_cnpj(cnpj: str) -> str:
    """Formata CNPJ com pontuação."""
    clean_cnpj = re.sub(r'\D', '', cnpj)
    return f"{clean_cnpj[:2]}.{clean_cnpj[2:5]}.{clean_cnpj[5:8]}/{clean_cnpj[8:12]}-{clean_cnpj[12:]}"
```

## Logging e Monitoramento

### Context Logging

```python
import contextvars

request_id = contextvars.ContextVar('request_id')

class ContextualError(Exception):
    """Exceção com contexto de requisição."""

    def __init__(self, message):
        self.request_id = request_id.get(None)
        super().__init__(f"[{self.request_id}] {message}")
```

### Métricas de Erro

```python
error_metrics = {
    'database_errors': 0,
    'validation_errors': 0,
    'bot_errors': 0,
    'total_errors': 0
}

def track_error(error_type):
    """Rastreia métricas de erro."""
    error_metrics[error_type] += 1
    error_metrics['total_errors'] += 1
```

## Configuração

### Error Handlers Globais

```python
from quart import Quart

app = Quart(__name__)

@app.errorhandler(ValidationError)
async def handle_validation_error(error):
    return {"error": "Validation failed", "message": str(error)}, 400

@app.errorhandler(DatabaseConnectionError)
async def handle_db_error(error):
    return {"error": "Database unavailable"}, 503
```

### Recovery Automático

```python
class RetryableError(Exception):
    """Exceção que permite retry automático."""

    def __init__(self, message, retry_after=60):
        super().__init__(message)
        self.retry_after = retry_after
```
