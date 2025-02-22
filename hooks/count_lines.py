#!/usr/bin/env python
import subprocess
import sys
import os

def count_changed_lines() -> tuple[str, int] | None:
    try:
        # Garante que o script rode no diretório raiz do repositório
        repo_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).strip().decode()
        os.chdir(repo_root)

        # Obtém o branch atual
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip().decode()

        # Obtém a quantidade de linhas adicionadas e removidas
        diff_output = subprocess.check_output(["git", "diff", "--numstat", "origin/main"]).decode()

        added_lines = 0
        removed_lines = 0

        for line in diff_output.splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                added_lines += int(parts[0]) if parts[0].isdigit() else 0
                removed_lines += int(parts[1]) if parts[1].isdigit() else 0

        total_lines_changed = added_lines + removed_lines
        message = f"[INFO] Total de linhas alteradas no branch '{branch}': {total_lines_changed}"
        if __name__ != "__main__":
            return message, total_lines_changed

        print(message)

        # Definir um limite opcional
        MAX_LINES = 500  # Altere conforme necessário
        if total_lines_changed > MAX_LINES:
            print(f"❌ O número de linhas alteradas ({total_lines_changed}) excede o limite de {MAX_LINES}. Revise as mudanças antes de commitar.")
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar git: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Define uma variável de ambiente para garantir que o script só rode uma vez
    if "PRE_COMMIT_RUNNING" not in os.environ:
        os.environ["PRE_COMMIT_RUNNING"] = "true"
        count_changed_lines()
