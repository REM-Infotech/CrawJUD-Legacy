# Dependencias do projeto CrawJUD-Bots

## Sumário

- [`Ferramentas de Desenvolvimento (Obrigatório)`](#ferramentas-de-desenvolvimento)
- [`API's`](#apis)
- [`Automatização`](#automatização)
- [`Gerenciamento de Arquivos`](#gerenciamento-de-arquivos)
- [`Manipulação de Dados/Documentos`](#manipulação-de-dadosdocumentos)
- [`Outras`](#outras)

## API's

- [`Flask`](https://flask.palletsprojects.com/en/stable/) _Framework Web_
- [`Flask-SocketIO`](https://flask-socketio.readthedocs.io/en/latest/) _Comunicação em tempo real_
- [`Flask-Mail`](https://pythonhosted.org/Flask-Mail/) _Envio de e-mails_
- [`Flask-Talisman`](https://github.com/GoogleCloudPlatform/flask-talisman) _Segurança_
- [`Flask-SQLAlchemy`](https://flask-sqlalchemy.palletsprojects.com/en/latest/) _ORM[\*](https://www.treinaweb.com.br/blog/o-que-e-orm)_
- [`Eventlet`](https://eventlet.net/doc/) _Servidor de SocketIO (Produção)_

## Automatização

- [`Celery`](https://docs.celeryproject.org/en/stable/) _Tarefas Assíncronas_
- [`Selenium`](https://www.selenium.dev/documentation/) _Automação de Navegadores_
- [`Webdriver-Manager`](https://github.com/SergeyPirogov/webdriver_manager) _Gerenciador de Webdrivers_
- [`Pywinauto`](https://pywinauto.readthedocs.io/en/latest/) _Automatização de aplicações Windows_
- [`Pyautogui`](https://pyautogui.readthedocs.io/en/latest/) _Automatização de mouse e teclado_

## Gerenciamento de Arquivos

- [`Google Cloud Storage`](https://googleapis.dev/python/storage/latest/index.html) _Armazenamento de arquivos_
- [`Google Auth`](https://google-auth.readthedocs.io/en/latest/) _Autenticação Google_

## Manipulação de Dados/Documentos

- [`Openpyxl`](https://openpyxl.readthedocs.io/en/stable/) _Manipulação de planilhas Excel_
- [`Pandas`](https://pandas.pydata.org/docs/) _Manipulação de dados_
- [`PyPDF`](https://pypdf.readthedocs.io/en/latest/) _Manipulação de PDF_
- [`Pillow`](https://pillow.readthedocs.io/en/stable/) _Manipulação de imagens_
- [`Python-Docx`](https://python-docx.readthedocs.io/en/latest/) _Manipulação de documentos Word_
- [`PyMuPDF`](https://pymupdf.readthedocs.io/en/latest/) _Manipulação de PDF_
- [`Watchdog`](https://python-watchdog.readthedocs.io/en/latest/) _Monitoramento de arquivos_

## Outras

- [`Tqdm`](https://tqdm.github.io/) _Barra de progresso_
- [`Psutil`](https://psutil.readthedocs.io/en/latest/) _Monitoramento de sistema_
- [`Bcrypt`](https://pypi.org/project/bcrypt/) _Criptografia de senhas_
- [`Python-SocketIO`](https://python-socketio.readthedocs.io/en/latest/) _Comunicação em tempo real_
- [`PyYAML`](https://pyyaml.org/wiki/PyYAMLDocumentation) _Manipulação de arquivos YAML_
- [`GitPython`](https://gitpython.readthedocs.io/en/stable/) _Manipulação de repositórios Git_
- [`PyGithub`](https://pygithub.readthedocs.io/en/latest/) _Integração com a API do GitHub_

## Ferramentas de Desenvolvimento

#### Comando de instalação de instalação

```bash
poetry install --with dev
```

> Disclaimer: para novas bibliotecas de desenvolvimento, usar o seguinte comando:

```bash
poetry add <_nome_da_biblioteca_> --group dev
```

- [isort](https://pycqa.github.io/isort/) _Formatação de imports_
- [Black](https://black.readthedocs.io/en/stable/) _Formatação de código_
- [Ruff](https://beta.ruff.rs/docs/) _Checagem de código_
- [Mypy](https://mypy.readthedocs.io/en/stable/) _Checagem de tipos_
- [pre-commit](https://pre-commit.com/) _Checagem de código antes do commit_
- [debugpy](https://github.com/microsoft/debugpy) _Depuração remota_
- [pytest](https://docs.pytest.org/en/stable/) _Testes unitários_
- [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) _Cobertura de testes_
- [pytest-mock](https://pytest-mock.readthedocs.io/en/latest/) _Mocking de objetos_
- [yamllint](https://yamllint.readthedocs.io/en/stable/) _Checagem de arquivos YAML_
- [pyproject-flake8](https://flake8.pycqa.org/en/latest/) _Checagem de estilo de código_
- [flake8-docstrings](https://pypi.org/project/flake8-docstrings/) _Checagem de docstrings_
