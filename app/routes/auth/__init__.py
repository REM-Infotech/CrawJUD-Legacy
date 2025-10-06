from flask import Blueprint, Response, jsonify, make_response

from app.decorators._api import CrossDomain

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/login", methods=["POST"])
@CrossDomain(methods=["POST", "OPTIONS"])
def login() -> Response:
    return make_response(jsonify({"message": "Login successful"}), 200)
