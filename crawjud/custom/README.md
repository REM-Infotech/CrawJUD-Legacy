# Custom - Funcionalidades Customizadas

Este módulo contém funcionalidades customizadas, extensões específicas do projeto e implementações personalizadas que não se encaixam nos módulos padrão do CrawJUD. Principalmente focado em customizações relacionadas ao Celery e adaptações específicas.

## Arquitetura

### Extensibilidade
O módulo custom permite:
- Customizações específicas do Celery
- Implementações específicas de clientes
- Funcionalidades experimentais
- Adaptações personalizadas
- Integrações customizadas

### Organização
As funcionalidades são organizadas por:
- Customizações do Celery
- Tipo de customização
- Cliente específico
- Funcionalidade experimental

## Customizações do Celery

### Custom Tasks
Tarefas Celery customizadas com comportamentos específicos:

```python
from celery import Task
from crawjud.celery_app import crawjud_app

class CustomTask(Task):
    """Tarefa base customizada com comportamentos específicos."""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Callback customizado para sucesso."""
        # Logging customizado
        logger.info(f"Tarefa {task_id} executada com sucesso")
        
        # Notificações específicas
        self.send_success_notification(retval, task_id)
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Callback customizado para falha."""
        # Logging de erro customizado
        logger.error(f"Tarefa {task_id} falhou: {exc}")
        
        # Tratamento específico de erro
        self.handle_custom_error(exc, task_id, args, kwargs)
    
    def send_success_notification(self, result, task_id):
        """Envia notificação de sucesso customizada."""
        # Implementação específica
        pass
    
    def handle_custom_error(self, exc, task_id, args, kwargs):
        """Trata erros de forma customizada."""
        # Implementação específica de recovery
        pass

@crawjud_app.task(base=CustomTask, bind=True)
def custom_bot_execution(self, bot_id, user_id, params):
    """Tarefa customizada para execução de bot."""
    try:
        # Lógica customizada de execução
        result = execute_custom_bot_logic(bot_id, user_id, params)
        return result
    except Exception as exc:
        # Retry com configuração customizada
        self.retry(exc=exc, countdown=60, max_retries=3)
```

### Custom Worker
Worker customizado com configurações específicas:

```python
from celery import Celery
from celery.signals import worker_ready, worker_shutdown

class CustomWorker:
    """Worker customizado com configurações específicas."""
    
    def __init__(self, app: Celery):
        self.app = app
        self.setup_custom_signals()
    
    def setup_custom_signals(self):
        """Configura sinais customizados."""
        @worker_ready.connect
        def worker_ready_handler(sender=None, **kwargs):
            """Handler para worker ready."""
            logger.info("Worker customizado iniciado")
            self.initialize_custom_resources()
        
        @worker_shutdown.connect
        def worker_shutdown_handler(sender=None, **kwargs):
            """Handler para worker shutdown."""
            logger.info("Worker customizado finalizando")
            self.cleanup_custom_resources()
    
    def initialize_custom_resources(self):
        """Inicializa recursos customizados."""
        # Setup de conexões específicas
        # Inicialização de caches
        # Configuração de drivers
        pass
    
    def cleanup_custom_resources(self):
        """Limpa recursos customizados."""
        # Fechamento de conexões
        # Cleanup de arquivos temporários
        # Finalização de drivers
        pass
```

### Custom Middleware
Middleware personalizado para o Celery:

```python
class CustomCeleryMiddleware:
    """Middleware customizado para tarefas Celery."""
    
    def __init__(self, app: Celery):
        self.app = app
        self.setup_middleware()
    
    def setup_middleware(self):
        """Configura middleware customizado."""
        @self.app.task_prerun.connect
        def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
            """Executado antes de cada tarefa."""
            logger.debug(f"Iniciando tarefa {task_id}")
            self.pre_task_setup(task_id, task, args, kwargs)
        
        @self.app.task_postrun.connect
        def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds):
            """Executado após cada tarefa."""
            logger.debug(f"Finalizando tarefa {task_id}")
            self.post_task_cleanup(task_id, task, retval, state)
    
    def pre_task_setup(self, task_id, task, args, kwargs):
        """Setup antes da execução da tarefa."""
        # Configuração de contexto
        # Setup de logging específico
        # Inicialização de recursos
        pass
    
    def post_task_cleanup(self, task_id, task, retval, state):
        """Cleanup após execução da tarefa."""
        # Limpeza de contexto
        # Finalização de recursos
        # Métricas customizadas
        pass
```

## Custom Processors

### Data Processor Customizado
```python
class CustomDataProcessor:
    """Processador de dados customizado."""
    
    def __init__(self, processing_rules: dict):
        self.rules = processing_rules
        self.transformers = self._load_transformers()
    
    async def process_data(self, raw_data: dict) -> dict:
        """Processa dados com regras customizadas."""
        processed_data = raw_data.copy()
        
        for rule_name, rule_config in self.rules.items():
            transformer = self.transformers.get(rule_name)
            if transformer:
                processed_data = await transformer.transform(
                    processed_data, 
                    rule_config
                )
        
        return processed_data
    
    def _load_transformers(self) -> dict:
        """Carrega transformadores disponíveis."""
        return {
            'normalize_names': NameNormalizer(),
            'format_dates': DateFormatter(),
            'extract_entities': EntityExtractor(),
            'validate_cpf_cnpj': DocumentValidator()
        }
```

## Custom Configurations

### Configuration Manager
```python
class CustomConfigManager:
    """Gerenciador de configurações customizadas."""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self._config_cache = {}
    
    async def load_client_config(self, client_id: str) -> dict:
        """Carrega configuração específica do cliente."""
        if client_id in self._config_cache:
            return self._config_cache[client_id]
        
        config_file = self.config_path / f"client_{client_id}.json"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = self._get_default_config()
        
        self._config_cache[client_id] = config
        return config
    
    async def save_client_config(self, client_id: str, config: dict):
        """Salva configuração do cliente."""
        config_file = self.config_path / f"client_{client_id}.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self._config_cache[client_id] = config
```

## Uso e Exemplos

### Implementação de Tarefa Customizada
```python
@crawjud_app.task(base=CustomTask, bind=True)
def process_judicial_data(self, data_list, processing_config):
    """Processa dados judiciais com configurações customizadas."""
    try:
        processor = CustomDataProcessor(processing_config)
        results = []
        
        for data_item in data_list:
            processed = await processor.process_data(data_item)
            results.append(processed)
        
        return {"status": "success", "results": results}
    except Exception as exc:
        self.retry(exc=exc, countdown=30)
```

### Configuração de Worker Customizado
```python
# Inicialização do worker customizado
from crawjud.celery_app import crawjud_app
from crawjud.custom import CustomWorker, CustomCeleryMiddleware

# Setup do worker customizado
custom_worker = CustomWorker(crawjud_app)
custom_middleware = CustomCeleryMiddleware(crawjud_app)

# Aplicar configurações customizadas
crawjud_app.conf.update(
    task_routes={
        'crawjud.custom.*': {'queue': 'custom_queue'},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=100
)
```

## Estrutura de Arquivos

- **Módulos Python** para customizações e ajustes finos
- **Configurações específicas** do Celery
- **Extensões customizadas** para requisitos específicos
- **Adaptações de comportamento** padrão das tarefas

## Benefícios

- **Flexibilidade**: Permite adaptações específicas sem modificar o core
- **Manutenibilidade**: Mantém customizações organizadas e isoladas
- **Escalabilidade**: Facilita adição de novas customizações
- **Testabilidade**: Permite testes isolados de funcionalidades customizadas
