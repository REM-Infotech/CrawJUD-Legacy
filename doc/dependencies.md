# Dependencies for the CrawJUD-Bots Project

## Summary

> For the Portuguese (Br) version, click [here](./dependencies-pt-br.md).

- [`Development Tools (Mandatory)`](#development-tools)
- [`APIs`](#apis)
- [`Automation`](#automation)
- [`File Management`](#file-management)
- [`Data/Document Handling`](#datadocument-handling)
- [`Others`](#others)

## APIs

- [`Flask`](https://flask.palletsprojects.com/en/stable/) _API Framework_
- [`Flask-SocketIO`](https://flask-socketio.readthedocs.io/en/latest/) _Real-time Communication_
- [`Flask-Mail`](https://pythonhosted.org/Flask-Mail/) _Email Sending_
- [`Flask-Talisman`](https://github.com/GoogleCloudPlatform/flask-talisman) _Security_
- [`Flask-SQLAlchemy`](https://flask-sqlalchemy.palletsprojects.com/en/latest/) _ORM[\*](https://www.treinaweb.com.br/blog/o-que-e-orm)_
- [`Eventlet`](https://eventlet.net/doc/) _SocketIO Server (Production)_

## Automation

- [`Celery`](https://docs.celeryproject.org/en/stable/) _Asynchronous Tasks_
- [`Selenium`](https://www.selenium.dev/documentation/) _Browser Automation_
- [`Webdriver-Manager`](https://github.com/SergeyPirogov/webdriver_manager) _Webdriver Manager_
- [`Pywinauto`](https://pywinauto.readthedocs.io/en/latest/) _Windows Application Automation_
- [`Pyautogui`](https://pyautogui.readthedocs.io/en/latest/) _Mouse and Keyboard Automation_

## File Management

- [`Google Cloud Storage`](https://googleapis.dev/python/storage/latest/index.html) _File Storage_
- [`Google Auth`](https://google-auth.readthedocs.io/en/latest/) _Google Authentication_

## Data/Document Handling

- [`Openpyxl`](https://openpyxl.readthedocs.io/en/stable/) _Excel Spreadsheet Manipulation_
- [`Pandas`](https://pandas.pydata.org/docs/) _Data Manipulation_
- [`PyPDF`](https://pypdf.readthedocs.io/en/latest/) _PDF Manipulation_
- [`Pillow`](https://pillow.readthedocs.io/en/stable/) _Image Manipulation_
- [`Python-Docx`](https://python-docx.readthedocs.io/en/latest/) _Word Document Manipulation_
- [`PyMuPDF`](https://pymupdf.readthedocs.io/en/latest/) _PDF Manipulation_
- [`Watchdog`](https://python-watchdog.readthedocs.io/en/latest/) _File Monitoring_

## Others

- [`Tqdm`](https://tqdm.github.io/) _Progress Bar_
- [`Psutil`](https://psutil.readthedocs.io/en/latest/) _System Monitoring_
- [`Bcrypt`](https://pypi.org/project/bcrypt/) _Password Hashing_
- [`Python-SocketIO`](https://python-socketio.readthedocs.io/en/latest/) _Real-time Communication_
- [`PyYAML`](https://pyyaml.org/wiki/PyYAMLDocumentation) _YAML File Handling_
- [`GitPython`](https://gitpython.readthedocs.io/en/stable/) _Git Repository Handling_
- [`PyGithub`](https://pygithub.readthedocs.io/en/latest/) _GitHub API Integration_

## Development Tools

#### Installation Command

> To install all development dependencies, use the following command:

```bash
poetry install --with dev
```

> Disclaimer: for new development libraries, use the following command:

```bash
poetry add <_library_name_> --group dev
```

#### Libraries:

- [`pre-commit`](https://pre-commit.com/) _Code Pre-commit Checks_

  > Note: This library eliminates the need for manual execution of libraries with `*`.<br>
  > Command for execution:

  ```bash
  pre-commit run --all-files
  ```

- [`yamllint`](https://yamllint.readthedocs.io/en/stable/) _YAML File Checks_
- [`isort*`](https://pycqa.github.io/isort/) _Import Sorting_
- [`Black*`](https://black.readthedocs.io/en/stable/) _Code Formatting_
- [`Ruff*`](https://beta.ruff.rs/docs/) _Code Checks_
- [`Mypy*`](https://mypy.readthedocs.io/en/stable/) _Type Checking_
- [`debugpy`](https://github.com/microsoft/debugpy) _Remote Debugging_

  > Disclaimer: This library is used in conjunction with the configurations in the [`launch.json`](../.vscode/launch.json) file.

- [`Pytest`](https://docs.pytest.org/en/stable/) _Unit Testing_

  > Pytest dependencies:

  - [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) _Test Coverage_
  - [pytest-mock](https://pytest-mock.readthedocs.io/en/latest/) _Object Mocking_

- [`Flake8*`](https://flake8.pycqa.org/en/latest/) _Code Style Checks_

  > Flake8 dependencies:

  - [flake8-docstrings](https://pypi.org/project/flake8-docstrings/) _Docstring Checks_
  - [pyproject-flake8](https://flake8.pycqa.org/en/latest/) _Allows loading configurations from the [`pyproject.toml`](../pyproject.toml) file_
