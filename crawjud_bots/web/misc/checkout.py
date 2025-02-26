"""Module to handle GitHub release tag checkout and comparison."""

# Função para atualizar para a tag da nova release
from os import environ

from dotenv_vault import load_dotenv
from github import Github

load_dotenv()
config_vals = environ

GITHUB_API_TOKEN = config_vals.get("GITHUB_API_TOKEN", "")
REPO_NAME = config_vals.get("REPO_NAME", "")
USER_GITHUB = config_vals.get("USER_GITHUB", "")


def checkout_release_tag() -> str:
    """Retrieve the latest GitHub release tag.

    Returns:
        str: The tag name of the latest release.

    """
    github = Github(GITHUB_API_TOKEN)
    repo = github.get_repo(REPO_NAME)
    releases = repo.get_releases()
    latest_release = sorted(releases, key=lambda release: release.created_at, reverse=True)[0]

    return latest_release.tag_name


def check_latest() -> bool:
    """Compare the local version with the latest release tag.

    Returns:
        bool: True if the version matches the latest release, otherwise False.

    """
    with open(".version") as f:
        version = f.read()

    latest = checkout_release_tag()

    return version == latest
