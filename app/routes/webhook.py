import eventlet

eventlet.monkey_patch()
import hashlib
import hmac
import json
import logging
from os import path
from pathlib import Path
from typing import Dict

from dotenv import dotenv_values
from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    jsonify,
    make_response,
    request,
)
from git import Repo

from ..misc.checkout import checkout_release_tag

wh = Blueprint("webhook", __package__)


# Endpoint para o webhook
@wh.post("/webhook")
def github_webhook() -> Response:  # pragma: no cover

    app = current_app
    data = request.json

    verify_signature(
        request.get_data(),
        app.config.get("WEBHOOK_SECRET"),
        request.headers.get("X-Hub-Signature-256"),
    )

    request_type = request.headers.get("X-GitHub-Event")

    if app.debug is True:
        with open("request.json", "w") as f:
            f.write(json.dumps(data))

        headers_data_json = {}

        headers_data = list(request.headers.items())

        for key, value in headers_data:
            headers_data_json.update({key: str(value)})

        with open("headers.json", "w") as f:
            f.write(json.dumps(headers_data_json))

    # Verifica se é uma nova release
    action = data.get("action")

    try:
        if request_type == "release" and action == "published":
            ref = data["release"]["tag_name"]
            # Alterna para a tag da nova release
            update_servers(f"refs/tags/{ref}")

        return make_response(
            jsonify({"message": "Release processada e atualizada"}), 200
        )

    except Exception as e:

        logging.exception(str(e))
        return make_response(jsonify({"message": "Evento ignorado"}), 500)


def update_servers(tag: str) -> None:  # pragma: no cover

    checkout_release(tag)

    path_fileversion = Path(path.join(Path(__file__).cwd(), ".version"))

    with path_fileversion.open("w") as f:
        f.write(checkout_release_tag())


def verify_signature(
    payload_body: Dict[str, str] = None,
    secret_token: str = None,
    signature_header: str = None,
) -> None:  # pragma: no cover
    """Verify that the payload was sent from GitHub by validating SHA256.

    Raise and return 403 if not authorized.

    Args:
        payload_body: original request body to verify (request.body())
        secret_token: GitHub app webhook token (WEBHOOK_SECRET)
        signature_header: header received from GitHub (x-hub-signature-256)
    """
    if not signature_header:
        raise abort(403, detail="x-hub-signature-256 header is missing!")
    hash_object = hmac.new(
        secret_token.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256,
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        raise abort(403, detail="Request signatures didn't match!")


def checkout_release(tag: str) -> None:  # pragma: no cover

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
    git.checkout(tag)
