# CrawJUD - RPA para Processos Judiciais

[![licença mit](https://img.shields.io/badge/licen%C3%A7a-MIT-blue.svg)](./LICENSE)
[![Python 3.11](https://shields.io/badge/python-3.11%20-green?logo=python)](https://python.org/downloads/release/python-3119/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

## Tecnologias

[![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://learn.microsoft.com/pt-br/virtualization/windowscontainers/quick-start/set-up-environment?tabs=dockerce)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/get-started)
[![Celery](https://img.shields.io/badge/celery-%23a9cc54.svg?style=for-the-badge&logo=celery&logoColor=ddf4a4)](https://docs.celeryq.dev/en/stable/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/en/2.0.x/)
[![Poetry](https://img.shields.io/badge/Poetry-430098?style=for-the-badge&logo=python&logoColor=white)](https://python-poetry.org/docs/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

## Descrição

CrawJUD é uma suíte de robôs de automação projetada para melhorar e agilizar processos judiciais. Construída com Flask e várias bibliotecas Python, CrawJUD tem como objetivo automatizar tarefas rotineiras, gerenciar dados de forma eficiente e fornecer integração perfeita com sistemas existentes.

_Total de linhas no código: `9523`_
_Última contagem: `10/12/2024 10:16`_

## Tabela de Conteúdo

- [Estrutura do Projeto](#estrutura-do-projeto)
- [Dependências](../doc/dependencies-pt-br.md)
- [Instalação](#instalação)
- [Uso](#uso)
- [Depuração](#depuração)
- [Contribuição](#contribuição)
- [Licença](#licença)

## Estrutura do Projeto

- [`app/`](./app/): Centraliza rotas, formulários e modelos Flask.

  - [`models/`](./app/models/): Contém modelos e ligações SQL.

  - [`Forms/`](./app/Forms/): Formulários do projeto, organizados por funcionalidade.

  - [`routes/`](./app/routes/): Rotas do projeto, organizadas por funcionalidade.

- [`bot/`](./bot/): Contém scripts e configurações relacionadas a robôs.

## Installation

Para configurar o projeto localmente, siga estas etapas:

1. **Clone o repositório:**

   ```bash
   git clone [URL do Repositório](./)
   cd CrawJUD-Bots
   ```

2. **Configure as variáveis de ambiente:**

   Configure conforme a documentação do [python-dotenv-vault](https://www.dotenv.org/docs/quickstart)

3. **Instale as dependências usando Poetry:**

   ```bash
   poetry install
   ```

4. **Execute a aplicação:**

   ```bash
   poetry run flask run
   ```

## Uso

Forneça instruções e exemplos de como usar a aplicação.

## Depuração

### Requisitos:

- **Cloudflare Tunnel (Obrigatório):** [Documentação do Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)

  > Se você tiver dúvidas sobre como configurar um Cloudflare Tunnel, assista [Este Vídeo](https://www.youtube.com/watch?v=Y0LTZZCyPko&t=123s)

## Contribuição

Infelizmente, ainda não estamos aceitando contribuições

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](./LICENSE) para detalhes.
