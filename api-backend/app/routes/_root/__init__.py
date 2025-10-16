from flask import (
    Response,
    current_app,
    jsonify,
    make_response,
    redirect,
    request,
    send_from_directory,
    url_for,
)

from app import app, root_app
from app._types import HealtCheck
from app.resources.extensions import db


@root_app.route("/health")
def health_check() -> HealtCheck:
    """Verifique status de saúde da aplicação.

    Returns:
        HealtCheck: HealtCheck

    """
    try:
        # Testa conexão com banco de dados
        db.session.execute(db.text("SELECT 1"))
        db_status = "ok"
        code_err = 200
    except Exception as e:
        app.logger.exception(f"Health check failed: {e}")
        db_status = "erro"
        code_err = 500

    return make_response(
        jsonify({
            "status": "ok" if db_status == "ok" else "erro",
            "database": db_status,
            "timestamp": str(db.func.now()),  # pyright: ignore[reportPossiblyUnboundVariable]
        }),
        code_err,
    )


@root_app.route("/", methods=["GET"])
def index() -> Response:
    """Redirect to the authentication login page.

    Returns:
        Response: A Quart redirect response to the login page.

    """
    return make_response(redirect(url_for("health_check")))


@root_app.route("/robots.txt")
def static_from_root() -> Response:
    return send_from_directory(current_app.static_folder, request.path[1:])  # pyright: ignore[reportArgumentType]


def register_blueprint() -> None:
    """Register a blueprint to the root_app.

    Args:
        blueprint: The blueprint to register.

    """
    from .auth import auth

    blueprints = [auth]
    for blueprint in blueprints:
        root_app.register_blueprint(blueprint)
