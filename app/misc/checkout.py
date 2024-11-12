# Função para atualizar para a tag da nova release
from github import Github
from dotenv import dotenv_values

config_vals = dotenv_values()

GITHUB_API_TOKEN = config_vals.get("GITHUB_API_TOKEN", "")
REPO_NAME = config_vals.get("REPO_NAME", "")
USER_GITHUB = config_vals.get("USER_GITHUB", "")


def checkout_release_tag() -> str:

    github = Github(GITHUB_API_TOKEN)
    repo = github.get_repo(REPO_NAME)
    releases = repo.get_releases()
    latest_release = sorted(
        releases, key=lambda release: release.created_at, reverse=True
    )[0]

    return latest_release.tag_name


def check_latest() -> bool:

    with open(".version", "r") as f:
        version = f.read()

    latest = checkout_release_tag()

    return version == latest
