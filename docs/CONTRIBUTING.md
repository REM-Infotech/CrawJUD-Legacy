# Manual de Contribuição e Testes

## Sumário

- [Introdução](#introdução)
- [Requisitos](#requisitos)
- [Como Contribuir](#como-contribuir)
- [Fluxo de Pull Request](#fluxo-de-pull-request)
- [Execução de Testes](#execução-de-testes)
- [Dicas e Boas Práticas](#dicas-e-boas-práticas)
- [Contato](#contato)

---

## Introdução

Este manual orienta colaboradores sobre como contribuir com o projeto CrawJUD e executar testes automatizados, garantindo qualidade e padronização no desenvolvimento.

## Requisitos

- Python 3.11+
- [Poetry](https://python-poetry.org/) ou `pip`
- Docker (opcional, para serviços auxiliares)
- Redis e/ou outros serviços conforme `.env`

## Como Contribuir

1. **Fork e Clone**

   - Faça um fork do repositório e clone para sua máquina:
     ```sh
     git clone https://github.com/seu-usuario/CrawJUD.git
     cd CrawJUD
     ```

2. **Crie uma branch**

   - Use nomes descritivos:
     ```sh
     git checkout -b feat/nome-da-feature
     ```

3. **Instale dependências**

   - Com Poetry:
     ```sh
     poetry install
     ```
   - Ou com pip:
     ```sh
     pip install -r requirements.txt
     ```

4. **Configure variáveis de ambiente**

   - Copie o arquivo `.env.copy` para `.env` e ajuste conforme necessário.

5. **Faça suas alterações**

   - Siga o padrão de código e utilize docstrings conforme o projeto.

6. **Execute os testes localmente**

   - Veja seção [Execução de Testes](#execução-de-testes).

7. **Commit e Push**

   - Escreva mensagens de commit claras e siga o padrão do projeto.

8. **Abra um Pull Request**
   - Descreva claramente as alterações e relacione issues, se aplicável.

## Fluxo de Pull Request

- Todos os PRs passam por análise de código e execução automática dos testes.
- Utilize o template de PR disponível.
- Corrija eventuais falhas apontadas pelo pre-commit ou CI.

## Execução de Testes

1. **Testes Unitários**

   - Execute:
     ```sh
     pytest
     ```
   - Ou, para cobertura:
     ```sh
     pytest --cov=crawjud
     ```

2. **Pre-commit**

   - Instale hooks:
     ```sh
     pre-commit install
     ```
   - Rode manualmente:
     ```sh
     pre-commit run --all-files
     ```

3. **Ambiente de Teste**
   - Utilize Docker Compose para serviços auxiliares, se necessário:
     ```sh
     docker compose -f compose-minio.yaml up -d
     ```

## Dicas e Boas Práticas

- Escreva funções e métodos com tipagem explícita.
- Utilize docstrings em português, seguindo o padrão do projeto.
- Prefira nomes de variáveis e funções descritivos.
- Consulte o [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) e siga as diretrizes de convivência.

## Contato

Dúvidas ou sugestões? Abra uma issue ou envie [e-mail](mailto:nicholas@robotz.dev) para o mantenedor
