"""Blueprint for handling GitHub webhook events."""

import hashlib
import hmac
import json
import logging
from typing import Dict

from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    jsonify,
    make_response,
    request,
)

from ..misc import update_servers

wh = Blueprint("webhook", __package__)


# Endpoint para o webhook
@wh.post("/webhook")
def github_webhook() -> Response:  # pragma: no cover
    """Handle incoming GitHub webhook events.

    Verifies the signature, processes release events, and updates servers accordingly.

    Returns:
        Response: JSON response indicating the result of the webhook processing.

    """
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

        return make_response(jsonify({"message": "Release processada e atualizada"}), 200)

    except Exception as e:
        logging.exception(str(e))
        return make_response(jsonify({"message": "Evento ignorado"}), 500)


def verify_signature(
    payload_body: Dict[str, str] = None,
    secret_token: str = None,
    signature_header: str = None,
) -> None:  # pragma: no cover
    """Verify that the payload was sent from GitHub by validating SHA256.

    Args:
        payload_body (Dict[str, str], optional): Original request body to verify.
        secret_token (str, optional): GitHub app webhook token.
        signature_header (str, optional): Signature header received from GitHub.

    Raises:
        abort(403): If the signature is missing or does not match.

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
