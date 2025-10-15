# Utils - Utilitários e Ferramentas Auxiliares

Este módulo contém utilitários e ferramentas auxiliares utilizadas em todo o sistema CrawJUD. As funcionalidades são organizadas por domínio e fornecem suporte a operações comuns como logging, armazenamento, geração de arquivos e automação web.

## Estrutura de Diretórios

### Logging (`logger/`)

Sistema de logging estruturado:

- **Handlers**: Diferentes tipos de saída de logs
- **Formatadores**: Formatação de mensagens
- **Configuração**: Setup automático de logging

### Storage (`storage/`)

Gerenciamento de armazenamento:

- **Credenciais**: Armazenamento seguro de credenciais
- **Arquivos**: Manipulação de arquivos
- **Cloud Storage**: Integração com Google Cloud Storage

### WebDriver (`webdriver/`)

Configuração e gerenciamento do Selenium:

- **Config**: Configurações de navegadores
- **Drivers**: Gerenciamento de drivers
- **Utilities**: Utilitários para automação web

### Geração de Arquivos (`xlsx_generator/`)

Criação de planilhas e documentos:

- **Models**: Modelos de dados para planilhas
- **Templates**: Templates para diferentes tipos de relatórios
- **Exportação**: Funções de exportação

### Interfaces (`interfaces/`)

Definições de interfaces e contratos:

- **Protocolos**: Interfaces TypedDict e Protocol
- **Tipos**: Definições de tipos customizados
- **Validação**: Validação de interfaces

### Modelos Auxiliares (`models/`)

Modelos de dados auxiliares:

- **DTOs**: Data Transfer Objects
- **Validadores**: Classes de validação
- **Conversores**: Conversão entre formatos

## Funcionalidades Principais

### Gerenciamento de Processos (`__init__.py`)

#### kill_browsermob()

```python
def kill_browsermob() -> None:
    """Finaliza processos relacionados ao BrowserMob Proxy."""
```

#### kill_chromedriver()

```python
def kill_chromedriver() -> None:
    """Finaliza processos relacionados ao ChromeDriver."""
```

### Formatadores (`formatadores.py`)

Utilidades para formatação de dados:

- Formatação de CPF/CNPJ
- Formatação de datas
- Normalização de textos
- Validação de formatos

### Configuração (`load_config.py`)

Carregamento de configurações:

- Leitura de arquivos de configuração
- Validação de parâmetros
- Merge de configurações
- Configurações por ambiente

### ReCaptcha (`recaptcha.py`)

Integração com serviços de captcha:

- Resolução automática de captchas
- Integração com APIs de terceiros
- Retry automático
- Logging de tentativas

### PJe Excel (`pje_savexlsx.py`)

Geração de planilhas específicas do PJe:

- Formatação de dados processuais
- Templates personalizados
- Validação de dados
- Exportação automática

## Middleware

### ProxyHeadersMiddleware

Middleware para tratamento de headers de proxy:

```python
class ProxyHeadersMiddleware:
    """Middleware para processar headers de proxy reverso."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Processamento de headers
        return await self.app(scope, receive, send)
```

## Padrões de Implementação

### Singleton para Configurações

```python
class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### Context Managers

```python
class WebDriverManager:
    def __enter__(self):
        self.driver = self._create_driver()
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()
```

### Decoradores Funcionais

```python
def retry(max_attempts=3, delay=1):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
```

## Configurações

### Logging

```python
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
```

### WebDriver

```python
WEBDRIVER_CONFIG = {
    'chrome': {
        'headless': True,
        'no_sandbox': True,
        'disable_dev_shm_usage': True,
        'disable_gpu': True
    },
    'firefox': {
        'headless': True,
        'disable_extensions': True
    }
}
```

## Uso Comum

### Logging

```python
from crawjud.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Operação realizada com sucesso")
```

### WebDriver

```python
from crawjud.utils.webdriver import WebDriverManager

with WebDriverManager() as driver:
    driver.get("https://example.com")
    # Operações com o driver
```

### Storage

```python
from crawjud.utils.storage import CloudStorage

storage = CloudStorage()
await storage.upload_file("local_file.pdf", "remote_path/file.pdf")
```

### Geração de Excel

```python
from crawjud.utils.xlsx_generator import MakeTemplates

generator = MakeTemplates()
excel_data = generator.create_pje_template(dados_processuais)
```

## Testes

### Configuração de Testes

- Mocks para WebDriver
- Fixtures para dados de teste
- Testes de integração
- Testes de performance

### Cobertura

- Cobertura mínima de 80%
- Testes unitários para cada utilitário
- Testes de integração para workflows
- Testes de stress para operações críticas
