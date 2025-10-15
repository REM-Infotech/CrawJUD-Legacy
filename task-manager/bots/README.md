# Bots - Robôs de Automação Judicial

O módulo de bots contém os robôs de automação para diversos sistemas judiciais brasileiros. Cada bot é especializado em um sistema específico e implementa funcionalidades como consulta de processos, protocolos, capas processuais e outras operações automatizadas.

## Sistemas Suportados

### Sistemas Judiciais Principais

#### PJe (Processo Judicial Eletrônico)

- **Diretório**: [`pje/`](./pje/README.md)
- **Descrição**: Sistema unificado de processo judicial eletrônico
- **Funcionalidades**: Capa processual, consulta de pauta, protocolos
- **Tribunais**: TRF, TRT, TRE e outros

#### ESAJ (Sistema de Automação da Justiça)

- **Diretório**: [`esaj/`](./esaj/README.md)
- **Descrição**: Sistema unificado de processo judicial eletrônico
- **Funcionalidades**: Consulta processual, capa de processos
- **Tribunal**: TJSP

#### PROJUDI (Processo Judicial Digital)

- **Diretório**: [`projudi/`](./projudi/README.md)
- **Descrição**: Sistema de processo judicial digital
- **Funcionalidades**: Capa processual, consultas
- **Tribunais**: Diversos TJs estaduais

#### E-Law

- **Diretório**: [`elaw/`](./elaw/README.md)
- **Descrição**: Sistema de gestão processual
- **Funcionalidades**: Cadastro, consultas, protocolos
- **Uso**: Escritórios e departamentos jurídicos

### Sistemas Auxiliares

#### JusBr

- **Diretório**: [`jusbr/`](./jusbr/README.md)
- **Descrição**: Portal de consultas jurídicas
- **Funcionalidades**: Consultas unificadas, jurisprudência

#### CSI (Central de Sistemas Integrados)

- **Diretório**: [`csi/`](./csi/README.md)
- **Descrição**: Sistema integrado de consultas
- **Funcionalidades**: Consultas centralizadas

#### Caixa Econômica Federal

- **Diretório**: [`caixa/`](./caixa/README.md)
- **Descrição**: Sistemas da Caixa para consultas
- **Funcionalidades**: Consultas financeiras e processuais

#### Calculadoras

- **Diretório**: [`calculadoras/`](./calculadoras/README.md)
- **Descrição**: Bots para cálculos automáticos
- **Funcionalidades**: Cálculos trabalhistas, previdenciários

## Arquitetura dos Bots

### Estrutura Base

Todos os bots seguem uma arquitetura padronizada:

```python
class BotBase:
    def __init__(self, credentials, config):
        self.driver = None
        self.credentials = credentials
        self.config = config

    async def initialize(self):
        """Inicializa o WebDriver"""
        pass

    async def authenticate(self):
        """Realiza autenticação no sistema"""
        pass

    async def execute_task(self, task_data):
        """Executa a tarefa específica"""
        pass

    async def cleanup(self):
        """Finaliza recursos"""
        pass
```

### Componentes Comuns

#### WebDriver Management

- Configuração automática do Selenium
- Gerenciamento de sessões
- Proxy e headers customizados
- Tratamento de captchas

#### Autenticação

- Login automático em sistemas
- Renovação de sessões
- Gerenciamento de cookies
- Tratamento de 2FA

#### Extração de Dados

- Parsing de HTML/XML
- Extração de PDFs
- OCR para imagens
- Estruturação de dados

#### Tratamento de Erros

- Retry automático
- Logging detalhado
- Notificações de falha
- Recovery de sessões

## Fluxo de Execução

1. **Inicialização**: Configuração do WebDriver e recursos
2. **Autenticação**: Login no sistema judicial
3. **Navegação**: Acesso às funcionalidades específicas
4. **Extração**: Coleta de dados processuais
5. **Processamento**: Estruturação e validação dos dados
6. **Armazenamento**: Salvamento em banco de dados
7. **Notificação**: Comunicação de resultados
8. **Limpeza**: Finalização de recursos

## Configuração

### Credenciais

Cada bot requer credenciais específicas:

- Usuário e senha do sistema
- Certificados digitais (quando aplicável)
- Tokens de API (quando disponível)
- Configurações de proxy

### Parâmetros

- Timeouts personalizados
- Configurações de retry
- Modos de execução (headless/visible)
- Configurações de logging

## Monitoramento

### Métricas

- Taxa de sucesso por bot
- Tempo médio de execução
- Erros e falhas
- Uso de recursos

### Logging

- Logs estruturados por execução
- Rastreamento de erros
- Screenshots de falhas
- Métricas de performance

## Desenvolvimento

### Criando Novos Bots

1. Implementar classe base
2. Definir métodos de autenticação
3. Implementar lógica de extração
4. Adicionar tratamento de erros
5. Configurar testes unitários
6. Documentar funcionalidades
