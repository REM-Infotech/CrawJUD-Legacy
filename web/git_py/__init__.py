"""Module for managing git operations and version updates using environment configuration."""

# from os import environ
# from pathlib import Path

# from dotenv_vault import load_dotenv
# from git import Repo

# # from github import Github
# # from github.Auth import Token

# # GITHUB_API_TOKEN = config_vals.get("GITHUB_API_TOKEN", "")
# # REPO_NAME = config_vals.get("REPO_NAME", "")
# # USER_GITHUB = config_vals.get("USER_GITHUB", "")
# cwd_dir = cwd_dir = Path(__file__).cwd().resolve()


# def _release_tag() -> str:
#     """Retrieve the latest git release tag.

#     Loads environment variables and fetches the latest tag from the remote repository.

#     Returns:
#         str: The latest release tag.

#     """
#     load_dotenv()
#     values = environ

#     user_git = values.get("USER_GITHUB")
#     token_git = values.get("GITHUB_API_TOKEN")
#     repo_git = values.get("REPO_NAME")

#     repo_remote = "".join(["https://", user_git, ":", token_git, "@", "github.com/", repo_git, ".git"])

#     git_path = cwd_dir.joinpath(".git").exists()
#     if not git_path:
#         repo = Repo.init()
#         origin = repo.create_remote("origin", repo_remote)
#         origin.fetch()

#     elif git_path:
#         repo = Repo(cwd_dir)

#     git = repo.git
#     git.fetch("--all", "--tags")
#     releases_tag = git.ls_remote("--tags", "--sort=committerdate").split("\n")[-1].split("tags/")[-1]

#     return releases_tag


# def check_latest() -> bool:
#     """Check if the current version matches the latest git tag.

#     Opens the .version file and compares its content against the latest tag.

#     Returns:
#         bool: True if the version is up-to-date, False otherwise.

#     """
#     with open(".version") as f:
#         version = f.read()

#     latest = _release_tag()

#     return version == latest


# def update_servers(tag: str) -> None:  # pragma: no cover
#     """Update the server version using the provided tag.

#     This function checks out a release and updates the .version file.

#     Args:
#         tag (str): The release tag to update to.

#     """
#     checkout_release(tag)

#     path_fileversion = cwd_dir.joinpath(".version")

#     with path_fileversion.open("w") as f:
#         f.write(_release_tag())


# def checkout_release(tag: str) -> None:  # pragma: no cover
#     """Checkout the git release specified by the tag.

#     Uses environment variables to initialize the repository if necessary, then
#     fetches all tags and checks out the specified tag.

#     Args:
#         tag (str): The release tag to checkout.

#     """
#     load_dotenv()

#     if environ.get("DEBUG", "False").lower() == "false":
#         values = environ
#         user_git = values.get("USER_GITHUB")
#         token_git = values.get("GITHUB_API_TOKEN")
#         repo_git = values.get("REPO_NAME")

#         repo_remote = "".join(["https://", user_git, ":", token_git, "@", "github.com/", repo_git, ".git"])

#         git_path = cwd_dir.joinpath(".git").exists()
#         if not git_path:
#             repo = Repo.init(Path(__file__).cwd())
#             origin = repo.create_remote("origin", repo_remote)
#             origin.fetch()

#         elif git_path:
#             repo = Repo(cwd_dir)

#         git = repo.git
#         git.fetch("--all", "--tags")

#         git.checkout(tag)


# def version_file() -> None:
#     """Ensure the version file is updated with the latest git release tag.

#     Reads the current version, compares it to the latest release tag, writes the new
#     tag if different, and triggers a checkout if necessary.
#     """
#     version_Path = Path(__file__).cwd().joinpath(".version")
#     version_ = None

#     if version_Path.exists():
#         with version_Path.open("r") as file_v:
#             version_ = str(file_v.read())

#     checkout_Version = _release_tag()

#     if (version_ and (version_ != checkout_Version)) or (not version_Path.exists()):
#         with open(".version", "w") as f:
#             f.write(checkout_Version)

#             if version_ != checkout_Version:
#                 checkout_release(f"refs/tags/{checkout_Version}")


# __all__ = [checkout_release, update_servers, check_latest, _release_tag]
