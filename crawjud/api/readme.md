# Documentação da Pasta API

## Introdução

A pasta `api/` é responsável por expor as funcionalidades do backend do CrawJUD por meio de endpoints RESTful, gerenciamento de autenticação, controle de rotas, namespaces e integração com módulos internos do sistema. Ela centraliza a comunicação entre clientes externos (frontends, automações, integrações) e os serviços internos, garantindo segurança, padronização e escalabilidade.

## Estrutura da Pasta

```
api
├───namespaces
│   ├───__init__.py
│   ├───bots.py
│   ├───files.py
│   └───logs.py
│
└───routes
    ├───bot
    │   ├───__init__.py
    │   └───launch.py
    ├───config
    │   ├───__init__.py
    │   ├───users.py
    └───execution
        ├───__init__.py
        └───schedules.py
```

- [**namespaces/**](./namespaces/__init__.py): Contém definições de namespaces para organizar os endpoints em grupos lógicos, facilitando a manutenção e a navegação na API.

- [**routes/**](./routes/__init__.py): Abriga os arquivos de rotas que definem os endpoints específicos para diferentes funcionalidades:
  - [**bot/**](./routes/bot/__init__.py): Rotas relacionadas ao gerenciamento e controle dos bots de automação.
  - [**config/**](./routes/config/__init__.py): Rotas para configuração do sistema, incluindo usuários, permissões e parâmetros globais.
  - [**execution/**](./routes/execution/__init__.py): Rotas para iniciar, monitorar e gerenciar execuções de tarefas automatizadas.

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
