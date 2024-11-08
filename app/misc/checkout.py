# Função para atualizar para a tag da nova release
import os
import git

from github import Github
from dotenv import dotenv_values

config_vals = dotenv_values()

GITHUB_API_TOKEN = config_vals.get("GITHUB_API_TOKEN", "")
REPO_NAME = config_vals.get("REPO_NAME", "")
USER_GITHUB = config_vals.get("USER_GITHUB", "")

repo_url = f"https://{USER_GITHUB}:{GITHUB_API_TOKEN}@github.com/{REPO_NAME}.git"
g = Github(GITHUB_API_TOKEN)

if __name__ != "__main__":
    from app import app


def format_path(REPO_NAME: str):

    if REPO_NAME is None:
        raise Exception("REPO_NAME IS NONE!!!!!")

    if "/" in REPO_NAME:
        file_p = REPO_NAME.split("/")[1]

    return os.path.join(os.path.abspath(os.sep), file_p)


def checkout_release_tag(tag_: str, debug: bool) -> str:

    LOCAL_REPO_PATH = config_vals.get("LOCAL_REPO_PATH", format_path(REPO_NAME))
    repo = git.Repo(LOCAL_REPO_PATH)
    try:

        if tag_ != repo.active_branch.name:
            # Abre o repositório local

            if not os.path.exists(LOCAL_REPO_PATH):
                git.Repo.clone_from(repo_url, LOCAL_REPO_PATH)

            # Busca e alterna para a tag da nova release
            if debug is False:

                repo.git.fetch("--all", "--tags")
                repo.git.checkout(f"{tag_}")

                app.logger.info(f"Atualizado para a tag: {tag_}")
                return os.path.join(LOCAL_REPO_PATH, ".version")

    except Exception as e:
        app.logger.info(f"Erro ao atualizar para a tag {tag_}: {e}")
        raise e


if __name__ == "__main__":

    LOCAL_REPO_PATH = config_vals.get("LOCAL_REPO_PATH", format_path(REPO_NAME))
    git.Repo.clone_from(repo_url, LOCAL_REPO_PATH)
