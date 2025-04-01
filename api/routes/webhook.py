"""Webhook module for handling GitHub events.

This module defines a Flask blueprint for processing GitHub webhook events.
Each endpoint verifies the incoming payload signature and handles events such as release.
Additional helper functions perform signature verification using HMAC and SHA256.
"""

# import hashlib  # Standard library module for hashing algorithms.
# import hmac  # Standard library module for keyed-hashing for message authentication.
# import logging

# from flask import Blueprint, Response, abort, current_app, jsonify, make_response, request

# from crawjud.utils import update_servers

# wh = Blueprint("webhook", __package__)
# logger = logging.getLogger(__name__)


# @wh.post("/webhook")
# def github_webhook() -> Response:
#     """Handle incoming GitHub webhook events.

#     This function verifies the HMAC signature of the request payload and
#     processes release events by triggering server updates.

#     Returns:
#         Response: A JSON response indicating if the release was processed and updated
#                   or if an error occurred.

#     Raises:
#         abort: In case of missing or invalid signature.

#     """
#     # Retrieve the current Flask application context.
#     app = current_app
#     data = request.json  # Get JSON data from the request.

#     # Verify the request's signature using the configured secret.
#     verify_signature(request.get_data(), app.config.get("WEBHOOK_SECRET"), request.headers.get("X-Hub-Signature-256"))

#     # Identify the type of event received from GitHub.
#     request_type = request.headers.get("X-GitHub-Event")

#     # Verifica se é uma nova release
#     action = data.get("action")

#     try:
#         if request_type == "release" and action == "published":
#             ref = data["release"]["tag_name"]
#             # Update servers by switching to the new release tag.
#             update_servers(f"refs/tags/{ref}")

#         return make_response(jsonify({"message": "Release processada e atualizada"}), 200)

#     except Exception as e:
#         logger.exception(str(e))
#         return make_response(jsonify({"message": "Evento ignorado"}), 500)


# def verify_signature(
#     payload_body: bytes,
#     secret_token: str,
#     signature_header: str,
# ) -> None:
#     """Verify that the incoming payload signature is valid.

#     This function computes the HMAC SHA256 signature of the payload using the
#     provided secret token and compares it to the signature provided in the header.

#     Args:
#         payload_body (bytes): The raw request payload.
#         secret_token (str): The secret token configured for validating the signature.
#         signature_header (str): The HMAC signature sent in the 'X-Hub-Signature-256' header.

#     Raises:
#         abort: With a 403 status if the signature header is missing or if the signature does not match.

#     """
#     if not signature_header:
#         # Abort if the signature header is missing.
#         raise abort(403, detail="x-hub-signature-256 header is missing!")
#     # Create a new HMAC object using the secret token and payload.
#     hash_object = hmac.new(secret_token.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256)
#     expected_signature = "sha256=" + hash_object.hexdigest()
#     # Compare the expected signature with the incoming signature safely.
#     if not hmac.compare_digest(expected_signature, signature_header):
#         raise abort(403, detail="Request signatures didn't match!")
