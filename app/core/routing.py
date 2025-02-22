"""Route registration and blueprint configuration module.

This module handles the registration of application routes and blueprints,
providing a centralized location for route management and error handling setup.
It dynamically imports route modules and configures them with the Quart application.
"""

from importlib import import_module

from quart import Quart


async def register_routes(app: Quart) -> None:
    """Register application's blueprints and error handlers with the Quart instance.

    This function manages the application's routing configuration by:
    1. Dynamically importing required route modules
    2. Registering blueprints for bot and webhook endpoints
    3. Setting up application-wide error handlers

    Args:
        app (Quart): The Quart application instance to configure

    Returns:
        None

    Note:
        Currently registers 'bot' and 'webhook' blueprints, and imports
        logs routes automatically.

    """
    async with app.app_context():
        # Dynamically import additional route modules as needed.
        import_module("app.routes.logs", package=__package__)
        import_module("app.routes", package=__package__)

    from app.routes.bot import bot
    from app.routes.webhook import wh

    # Register the blueprints for bot and webhook endpoints.
    app.register_blueprint(wh)
    app.register_blueprint(bot)
