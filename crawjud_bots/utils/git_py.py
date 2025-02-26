"""Manages Git repository operations and version control tasks for the application.

This module provides functionality for interacting with Git repositories, including version
checking, tag management, and repository updates. It uses environment variables for configuration.
"""

from os import environ
from pathlib import Path

from dotenv_vault import load_dotenv
from git import Repo

cwd_dir = Path(__file__).cwd().resolve()


def _release_tag() -> str:
    """Fetch the most recent release tag from the configured remote Git repository.

    Connects to the Git repository using configured credentials and retrieves the latest tag,
    intended for version tracking and updates.

    Returns:
        The most recent release tag string.

    Raises:
        EnvironmentError: If required Git configuration variables are missing.

    """
    load_dotenv()
    values = environ

    user_git = values.get("USER_GITHUB")
    token_git = values.get("GITHUB_API_TOKEN")
    repo_git = values.get("REPO_NAME")

    repo_remote = "".join(["https://", user_git, ":", token_git, "@", "github.com/", repo_git, ".git"])

    git_path = cwd_dir.joinpath(".git").exists()
    if not git_path:
        repo = Repo.init()
        origin = repo.create_remote("origin", repo_remote)
        origin.fetch()

    elif git_path:
        repo = Repo(cwd_dir)

    git = repo.git
    git.fetch("--all", "--tags")
    releases_tag = git.ls_remote("--tags", "--sort=committerdate").split("\n")[-1].split("tags/")[-1]

    return releases_tag


def check_latest() -> bool:
    """Compare current version against the latest release tag to determine if updates exist.

    Reads the local version file and compares it with the latest release tag from the remote
    repository to check if the local installation is up-to-date.

    Returns:
        True if current version matches latest release, False otherwise.

    """
    with open(".version") as f:
        version = f.read()

    latest = _release_tag()

    return version == latest


def update_servers(tag: str) -> None:
    """Update servers to the specified release tag.

    Args:
        tag (str): The release tag to update to.

    """
    checkout_release(tag)

    path_fileversion = cwd_dir.joinpath(".version")

    with path_fileversion.open("w") as f:
        f.write(_release_tag())


def checkout_release(tag: str) -> None:
    """Checkout the specified release tag in the Git repository.

    Args:
        tag (str): The release tag to checkout.

    """
    load_dotenv()

    if environ.get("DEBUG", "False").lower() == "False":
        values = environ
        user_git = values.get("USER_GITHUB")
        token_git = values.get("GITHUB_API_TOKEN")
        repo_git = values.get("REPO_NAME")

        repo_remote = "".join(["https://", user_git, ":", token_git, "@", "github.com/", repo_git, ".git"])

        git_path = cwd_dir.joinpath(".git").exists()
        if not git_path:
            repo = Repo.init(Path(__file__).cwd())
            origin = repo.create_remote("origin", repo_remote)
            origin.fetch()

        elif git_path:
            repo = Repo(cwd_dir)

        git = repo.git
        git.fetch("--all", "--tags")

        git.checkout(tag)


def version_file() -> None:
    """Update the local version file with the latest release tag.

    If the version file does not exist or differs from the latest release tag,
    it updates the file and checks out the corresponding release.
    """
    version_path = Path(__file__).cwd().joinpath(".version")
    version_ = None

    if version_path.exists():
        with version_path.open("r") as file_v:
            version_ = str(file_v.read())

    checkout_version = _release_tag()

    if (version_ and (version_ != checkout_version)) or (not version_path.exists()):
        with open(".version", "w") as f:
            f.write(checkout_version)

            if version_ != checkout_version:
                checkout_release(f"refs/tags/{checkout_version}")


__all__ = [checkout_release, update_servers, check_latest, _release_tag]
