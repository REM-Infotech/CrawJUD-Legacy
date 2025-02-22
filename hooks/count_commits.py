#!/usr/bin/env python
import subprocess
import sys
import os

def count_branch_commits() -> int | None:
    try:
        # Garante que o script rode no diretório raiz do repositório
        repo_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).strip().decode()
        os.chdir(repo_root)

        # Obtém o branch atual
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip().decode()

        # Conta o número de commits entre a branch atual e main
        commit_count = int(subprocess.check_output(
            ["git", "rev-list", "--count", f"origin/main..{branch}"]
        ).decode().strip())

        message = f"[INFO] Total de commits no branch '{branch}': {commit_count}"

        if __name__ != "__main__":
            return message

        print(message)

        # Definir um limite opcional
        MAX_COMMITS = 10  # Altere conforme necessário
        if commit_count > MAX_COMMITS:
            print(f"[ERROR] O número de commits ({commit_count}) excede o limite de {MAX_COMMITS}. Considere fazer um rebase.")
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar git: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Define uma variável de ambiente para garantir que o script só rode uma vez
    if "PRE_COMMIT_RUNNING" not in os.environ:
        os.environ["PRE_COMMIT_RUNNING"] = "true"
        count_branch_commits()
