
# CrawJUD - Robôs de Automação
[![license mit](https://img.shields.io/badge/licence-MIT-blue.svg)](./LICENSE)
[![Python 3.11](https://shields.io/badge/python-3.11%20-green?logo=python)](https://python.org/downloads/release/python-3119/)

## Requisitos do projeto

### Setup de ambiente:

- [`PPA DeadSnakes | Apenas Linux`](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa#ppa-install)
    > Verificar qual sua distro para o comando correto da instalação do PPA e instalação do python 3.11
    ### No ubuntu e debian (Normalmente utilizados para projetos):
    - `sudo add-apt-repository ppa:deadsnakes/ppa`
    - `sudo apt update`
    - `sudo apt install python3.11 python3.11-venv default-libmysqlclient-dev build-essential`

- [`Dependências do Projeto`](./requirements.txt), estarão em `requirements.txt`

## Como rodar na minha máquina?

#### Instalação do `venv (Virtual Environment)`
> Caso opte por usar um nome personalizado, adicionar o mesmo no `.gitignore` para a pasta não subir para o repositório
- `python3.11 -m venv .venv` 
ou
- `python3.11 -m venv .{nomepersonalizado}` 

#### No Windows:
> Necessário habilitar execução de scripts `.ps1` da [Microsoft](https://learn.microsoft.com/pt-br/powershell/module/microsoft.powershell.core/about/about_execution_policies?view=powershell-7.4)
- `.venv/Scripts/activate`
- `python -m pip install -r requirements.txt`

#### No Linux:

- `source .venv/bin/activate`
- `python -m pip install -r requirements.txt`


## Estrutura do projeto

- [`APP`](./app/): É a pasta onde fica centralizado rotas, formulários e models do Flask

#### A partir de `/app`, teremos:
- [`Models`](./app/models/): Onde ficam os models e bind's do SQL.
    - `bases/`: Onde ficam as bases para evitar criação de base para cada SGBD diferente
    - `sqlite3/`, `mysqld/`, `oracle/`, etc: Onde ficam as binds para os databases respectivos

- [`Forms`](./app/Forms/): Formulários do projeto, sempre mantendo separados por funções, como, por exemplo:
    - pass

- [`Routes`](./app/routes/): Formulários do projeto, sempre mantendo separados por funções, como, por exemplo:
    - pass


## Como depurar em minha máquina?

### Requisitos:


#### [Cloudflare Tunnel (`Obrigatório`)](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)
> Caso tenha alguma dúvida de como configurar um Tunnel Cloudflare, veja [`Esse Video`](https://www.youtube.com/watch?v=Y0LTZZCyPko&t=123s)

#### Arquivo `.env`

```python

## URL do FRONT
DEBUG = ""
PORT = ""
TOKEN_IP2 = ""


url_web = ""
NAMESERVER = ""
HOST = ""

credentials_dict = ""

TUNNEL_ID =""
CREDENTIALS_TUNNEL = ""

MAIL_SERVER = ""
MAIL_PORT = ""
MAIL_USERNAME = ""
MAIL_PASSWORD = ""
MAIL_DEFAULT_SENDER = ""

## SQL Config
login = ""
password = ""
dbhost = ""
database = ""

credentials_dict = '{
  "type": "info da service account GCS",
  "project_id": "info da service account GCS",
  "private_key_id": "info da service account GCS",
  "private_key": "info da service account GCS",
  "client_email": "info da service account GCS",
  "client_id": "info da service account GCS",
  "auth_uri": "info da service account GCS",
  "token_uri": "info da service account GCS",
  "auth_provider_x509_cert_url": "info da service account GCS",
  "client_x509_cert_url": "info da service account GCS",
  "universe_domain": "info da service account GCS"
}'


```
