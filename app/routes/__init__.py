"""App routes."""

from flask import Flask, Response, make_response, redirect, url_for


def register_routes(app: Flask) -> None:
    """Registra as rotas do aplicativo."""
    from .api import api
    from .auth import auth

    blueprints = [auth, api]

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    @app.route("/", methods=["GET"])
    def index() -> Response:
        """Rota Index.

        Returns:
            Response: Redireciona para a rota de saúde (/api/health).

        """
        return make_response(redirect(url_for("api.health")))
