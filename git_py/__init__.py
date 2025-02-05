"""Initialization module for git_py package.

Provides functions to manage Git repository tags and handle versioning.
"""

from os import environ
from pathlib import Path

from dotenv_vault import load_dotenv
from git import Repo

# from github import Github
# from github.Auth import Token

# GITHUB_API_TOKEN = config_vals.get("GITHUB_API_TOKEN", "")
# REPO_NAME = config_vals.get("REPO_NAME", "")
# USER_GITHUB = config_vals.get("USER_GITHUB", "")
cwd_dir = Path(__file__).cwd().resolve()


def _release_tag() -> str:
    """Retrieve the latest release tag from the remote Git repository.

    Returns:
        str: The latest release tag.

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

    # token_github = Token(GITHUB_API_TOKEN)
    # github = Github(token_github)
    # repo = github.get_repo(REPO_NAME)
    # releases = repo.get_releases()

    # debug = config_vals.get("DEBUG", "False").lower() in ("true")

    # if debug is False:
    #     releases = list(filter(lambda release: "stable" in release.tag_name, releases))

    # latest_release = sorted(
    #     releases, key=lambda release: release.created_at, reverse=True
    # )[0]

    return releases_tag


def check_latest() -> bool:
    """Check if the current version matches the latest release tag.

    Returns:
        bool: True if the current version is up-to-date, False otherwise.

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
    version_Path = Path(__file__).cwd().joinpath(".version")  # noqa: N806
    version_ = None

    if version_Path.exists():
        with version_Path.open("r") as file_v:
            version_ = str(file_v.read())

    checkout_Version = _release_tag()  # noqa: N806

    if (version_ and (version_ != checkout_Version)) or (not version_Path.exists()):
        with open(".version", "w") as f:
            f.write(checkout_Version)

            if version_ != checkout_Version:
                checkout_release(f"refs/tags/{checkout_Version}")


__all__ = [checkout_release, update_servers, check_latest, _release_tag]
