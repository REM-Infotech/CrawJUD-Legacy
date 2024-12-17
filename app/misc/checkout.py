# Função para atualizar para a tag da nova release
from dotenv import dotenv_values
from github import Github
from github.Auth import Token

config_vals = dotenv_values()

GITHUB_API_TOKEN = config_vals.get("GITHUB_API_TOKEN", "")
REPO_NAME = config_vals.get("REPO_NAME", "")
USER_GITHUB = config_vals.get("USER_GITHUB", "")


def checkout_release_tag() -> str:

    token_github = Token(GITHUB_API_TOKEN)
    github = Github(auth=token_github)
    repo = github.get_repo(REPO_NAME)
    releases = repo.get_releases()

    debug = config_vals.get("DEBUG", "False").lower() in ("true")

    if debug is False:  # pragma: no cover
        releases = list(filter(lambda release: "stable" in release.tag_name, releases))

    latest_release = sorted(
        releases, key=lambda release: release.created_at, reverse=True
    )[0]

    return latest_release.tag_name


def check_latest() -> bool:

    with open(".version", "r") as f:
        version = f.read()

    latest = checkout_release_tag()

    return version == latest
