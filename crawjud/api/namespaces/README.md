# API Namespaces - Agrupamento de Rotas

Este diretório contém os namespaces da API, que são agrupamentos lógicos de rotas relacionadas. Os namespaces facilitam a organização e documentação automática da API.

## Conceito de Namespaces

Namespaces no CrawJUD são utilizados para:
- Organizar endpoints relacionados
- Documentação automática da API
- Versionamento de endpoints
- Aplicação de middlewares específicos

## Estrutura

### Organização por Funcionalidade
Cada namespace agrupa endpoints que compartilham:
- Domínio de negócio
- Modelo de dados
- Autenticação/autorização
- Versionamento

### Documentação Automática
Os namespaces facilitam a geração de documentação através de:
- Swagger/OpenAPI
- Descrições estruturadas
- Exemplos de uso
- Schemas de validação

## Implementação

### Estrutura Base
```python
from quart import Namespace

namespace = Namespace(
    'nome',
    description='Descrição do namespace',
    path='/api/v1/namespace'
)

@namespace.route('/endpoint')
async def endpoint():
    """Documentação do endpoint."""
    pass
```

### Configuração
- Prefixos de URL consistentes
- Versionamento através de paths
- Middleware aplicado por namespace
- Documentação estruturada

## Uso

Os namespaces são registrados automaticamente na aplicação principal e utilizados para organizar a documentação e estrutura da API.