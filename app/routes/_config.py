from flask import Flask


def register_routes(app: Flask) -> Flask:
    from .api import api
    from .auth import auth

    blueprints = [auth, api]

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    return app
