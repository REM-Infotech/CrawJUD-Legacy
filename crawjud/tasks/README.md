# Tasks - Tarefas Assíncronas com Celery

Este módulo implementa o sistema de tarefas assíncronas utilizando Celery. As tarefas permitem que operações demoradas (como execução de bots) sejam processadas em background, mantendo a responsividade da API.

## Arquitetura Celery

### Componentes
- **Worker**: Processo que executa as tarefas
- **Broker**: Redis como broker de mensagens
- **Backend**: Redis para armazenar resultados
- **Beat**: Agendador para tarefas periódicas

### Configuração
```python
# celery_app.py
app = Celery('crawjud')
app.config_from_object('crawjud.celeryconfig')
```

## Tipos de Tarefas

### Execução de Bots
Tarefas principais para execução de robôs:
- Inicialização de bots
- Processamento de dados
- Geração de relatórios
- Notificações de resultado

### Tarefas de Manutenção
Tarefas de housekeeping do sistema:
- Limpeza de logs antigos
- Backup de dados
- Verificação de saúde
- Sincronização de dados

### Tarefas Agendadas
Tarefas executadas periodicamente:
- Relatórios automáticos
- Sincronização com sistemas externos
- Monitoramento de status
- Limpeza de cache

## Estrutura de Diretórios

### Mail (`mail/`)
Tarefas relacionadas ao envio de emails:
- **Templates**: Templates HTML para emails
- **Envio**: Tarefas de envio assíncrono
- **Notificações**: Alertas e notificações

## Implementação de Tarefas

### Decorador @task
```python
from celery import current_app

@current_app.task(bind=True)
def execute_bot(self, bot_id, user_id, parameters):
    """Executa um bot específico de forma assíncrona.
    
    Args:
        bot_id (int): ID do bot a ser executado
        user_id (int): ID do usuário solicitante
        parameters (dict): Parâmetros de execução
        
    Returns:
        dict: Resultado da execução
    """
    try:
        # Lógica de execução do bot
        result = run_bot(bot_id, parameters)
        return {'status': 'success', 'result': result}
    except Exception as exc:
        # Log do erro e retry
        self.retry(exc=exc, countdown=60, max_retries=3)
```

### Configurações de Retry
```python
@current_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def resilient_task(self):
    """Tarefa com retry automático."""
    pass
```

## Monitoramento

### Status de Tarefas
```python
from celery.result import AsyncResult

result = AsyncResult(task_id)
status = result.status  # PENDING, SUCCESS, FAILURE, RETRY, REVOKED
```

### Métricas
- Número de tarefas ativas
- Taxa de sucesso/falha
- Tempo médio de execução
- Uso de recursos

## Padrões de Uso

### Chain de Tarefas
```python
from celery import chain

# Execução sequencial
workflow = chain(
    prepare_data.s(data),
    process_data.s(),
    generate_report.s()
)
result = workflow.apply_async()
```

### Group de Tarefas
```python
from celery import group

# Execução paralela
parallel_tasks = group(
    execute_bot.s(bot1_id, params),
    execute_bot.s(bot2_id, params),
    execute_bot.s(bot3_id, params)
)
result = parallel_tasks.apply_async()
```

## Exemplo de Uso

Implemente novas tarefas criando funções decoradas com `@crawjud_app.task`:

```python
from crawjud.celery_app import crawjud_app

@crawjud_app.task(bind=True)
def nova_tarefa(self, parametros):
    """Nova tarefa customizada."""
    # Implementação da tarefa
    return resultado
```
