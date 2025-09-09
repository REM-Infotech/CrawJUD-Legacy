# Documentação da Pasta API

## Introdução

A pasta `api/` é responsável por expor as funcionalidades do backend do CrawJUD por meio de endpoints RESTful, gerenciamento de autenticação, controle de rotas, namespaces e integração com módulos internos do sistema. Ela centraliza a comunicação entre clientes externos (frontends, automações, integrações) e os serviços internos, garantindo segurança, padronização e escalabilidade.

## Estrutura da Pasta

├── [`__init__.py`](./__init__.py): Inicializa o pacote e configurações globais da API.
├── [`namespaces/`](./namespaces/): Define namespaces lógicos para organização dos endpoints e recursos.
│ ├── [`bots.py`](./namespaces/bots.py): Gerencia operações relacionadas aos robôs.
│ ├── [`files.py`](./namespaces/files.py): Manipula arquivos e operações de upload/download.
│ ├── [`logs.py`](./namespaces/logs.py): Disponibiliza logs de execução e auditoria.
│ ├── [`notifications.py`](./namespaces/notifications.py): Gerencia notificações do sistema.
│ └── [`system.py`](./namespaces/system.py): Fornece informações e operações do sistema.
├── [`routes/`](./routes/): Implementa as rotas principais da API.
│ ├── [`auth.py`](./routes/auth.py): Endpoints de autenticação e autorização.
│ ├── [`credentials.py`](./routes/credentials.py): Gerenciamento de credenciais de acesso.
│ ├── [`dashboard.py`](./routes/dashboard.py): Dados e operações do dashboard administrativo.
│ ├── [`bot/`](./routes/bot/): Métodos e rotas específicas para execução e controle de bots.
│ │ ├── [`launch.py`](./routes/bot/launch.py): Métodos auxiliares para inicialização de bots.
│ └── [`config/`](./routes/config/): Rotas de configuração e gerenciamento de usuários.
│ ├── [`users.py`](./routes/config/users.py): Operações de cadastro, consulta e atualização de usuários.
│ └── [`execution/`](./routes/execution/): Controle de execuções e agendamentos.
│ ├── [`schedules.py`](./routes/execution/schedules.py): Gerenciamento de tarefas agendadas.

## Funcionamento e Lógica

- **Autenticação e Segurança:**  
  Utiliza JWT e validação de sessão para proteger endpoints sensíveis, garantindo que apenas usuários autenticados possam acessar recursos restritos.

- **Organização Modular:**  
  Os namespaces e subpastas permitem separar responsabilidades, facilitando manutenção, testes e extensibilidade.

- **Gerenciamento de Bots:**  
  Permite iniciar, monitorar e controlar robôs de automação via API, além de consultar status, logs e resultados.

- **Gerenciamento de Arquivos:**  
  Suporta upload, download e manipulação de arquivos necessários para os fluxos automatizados.

- **Logs e Auditoria:**  
  Disponibiliza endpoints para consulta de logs de execução, facilitando o acompanhamento e troubleshooting.

- **Notificações e Dashboard:**  
  Integra notificações em tempo real e fornece dados para dashboards administrativos.

## Exemplo de Uso

- **Autenticação:**  
  Realize login via endpoint `/auth` para obter um token JWT.
- **Execução de Bot:**  
  Dispare a execução de um robô via rota `/bot/launch` e acompanhe o status pelo endpoint de logs.
- **Gerenciamento de Usuários:**  
  Utilize as rotas em `/config/users` para cadastrar ou atualizar usuários do sistema.

## Observações

- Todas as rotas seguem convenções REST e retornam respostas em JSON.
- A estrutura modular facilita a adição de novos recursos sem impactar funcionalidades existentes.
- Consulte a documentação de cada submódulo para
