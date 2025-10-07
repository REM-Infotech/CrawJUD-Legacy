from flask import Flask


def register_routes(app: Flask) -> Flask:
    from .auth import auth

    blueprints = [auth]

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    return app
