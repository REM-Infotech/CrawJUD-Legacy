from flask import request, jsonify
from app import app
import json

from ..misc.checkout import checkout_release_tag


# Endpoint para o webhook
@app.route("/webhook", methods=["POST"])
def github_webhook():

    data = request.json
    request_type = request.headers.get("X-GitHub-Event")

    with open("request.json", "w") as f:
        f.write(json.dumps(data))

    # Verifica se é uma nova release
    action = data.get("action")
    ref = data["release"]["tag_name"]
    version_file = None
    try:
        if request_type == "release" and action == "published":
            ref = data["release"]["tag_name"]
            # Alterna para a tag da nova release
            version_file = str(checkout_release_tag(f"refs/tags/{ref}"))

        return jsonify({"message": "Release processada e atualizada"}), 200

    except Exception as e:

        app.logger.error(str(e))
        return jsonify({"message": "Evento ignorado"}), 500

    finally:

        if version_file:
            with open(version_file, "w") as f:
                f.write(ref)
