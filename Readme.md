# CrawJUD - RPA for Judicial Processes

[![Celery](https://img.shields.io/badge/celery-%23a9cc54.svg?style=for-the-badge&logo=celery&logoColor=ddf4a4)](https://docs.celeryq.dev/en/stable/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://quart.palletsprojects.com/en/stable/)
[![Poetry](https://img.shields.io/badge/Poetry-430098?style=for-the-badge&logo=python&logoColor=white)](https://python-poetry.org/docs/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

[![License MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](./LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python 3.13](https://shields.io/badge/python-3.13%20-green?logo=python)](https://python.org/downloads/release/python-3132/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

## Description

CrawJUD is a suite of automation robots designed to streamline and enhance judicial processes. Built with Flask and various Python libraries, CrawJUD aims to automate routine tasks, manage data efficiently, and provide seamless integration with existing systems.

_Total lines: `14551`_
_Last count: `22/02/2025 11:00 (América\São Paulo)`_

## Table of Contents

> Portuguese (Br) version available [here](./doc/Readme-pt-br.md)

- [Project Structure](#project-structure)
- [Dependencies](./doc/dependencies.md)
- [Installation](#installation)
- [Usage](#usage)
- [Debugging](#debugging)
- [Contributing](#contributing)
- [Project Pull Request Guidelines](./PR_GUIDELINES.md)
- [License](#license)

## Project Structure

- [`app/`](./app/): Centralizes routes, forms, and Flask models.

  - [`models/`](./app/models/): Contains models and SQL bindings.

  - [`Forms/`](./app/Forms/): Project forms, organized by functionality.

  - [`routes/`](./app/routes/): Project routes, organized by functionality.

  > For more details, check the [app structure documentation](./doc/app_structure.md).

- [`bot/`](./bot/): Contains bot-related scripts and configurations.

## Installation

To set up the project locally, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone [Repository URL](./)
   cd CrawJUD-Bots
   ```

2. **Set up the environment variables:**

   Create a `.env` file based on the provided [.env.vault](http://_vscodecontentref_/0) template.

3. **Install dependencies using Poetry:**

   ```bash
   poetry install
   ```

4. **Run the application:**

   ```bash
   poetry run flask run
   ```

## Usage

Provide instructions and examples on how to use the application.

## Debugging

### Requirements:

- **Cloudflare Tunnel (Required):** [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)

  > If you have any doubts on how to set up a Cloudflare Tunnel, watch [This Video](https://www.youtube.com/watch?v=Y0LTZZCyPko&t=123s)

## Contributing

Unfortunately we are not yet accepting contributions

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
