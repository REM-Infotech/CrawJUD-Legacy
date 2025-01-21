# Função para atualizar para a tag da nova release
from pathlib import Path

from dotenv import dotenv_values
from git import Repo

# from github import Github
# from github.Auth import Token


def checkout_release_tag() -> str:

    values = dotenv_values()

    user_git = values.get("USER_GITHUB")
    token_git = values.get("GITHUB_API_TOKEN")
    repo_git = values.get("REPO_NAME")

    repo_remote = "".join(
        ["https://", user_git, ":", token_git, "@", "github.com/", repo_git, ".git"]
    )

    git_path = Path(__file__).cwd().resolve().joinpath(".git").exists()
    if not git_path:

        repo = Repo.init(Path(__file__).cwd())
        origin = repo.create_remote("origin", repo_remote)
        origin.fetch()

    elif git_path:
        repo = Repo(Path(__file__).cwd().resolve())

    git = repo.git
    git.fetch("--all", "--tags")
    releases_tag = (
        git.ls_remote("--tags", "--sort=committerdate")
        .split("\n")[-1]
        .split("tags/")[-1]
    )

    return releases_tag


def check_latest() -> bool:

    with open(".version", "r") as f:
        version = f.read()

    latest = checkout_release_tag()

    return version == latest
