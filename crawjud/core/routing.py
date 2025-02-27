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
        import_module("crawjud.routes.logs", package=__package__)
        import_module("crawjud.routes", package=__package__)

    from crawjud.routes.auth import auth
    from crawjud.routes.bot import bot
    from crawjud.routes.config import admin, supersu, usr
    from crawjud.routes.credentials import cred
    from crawjud.routes.dashboard import dash
    from crawjud.routes.execution import exe
    from crawjud.routes.logs import logsbot

    listBlueprints = [bot, auth, logsbot, exe, dash, cred, admin, supersu, usr]  # noqa: N806

    for bp in listBlueprints:
        app.register_blueprint(bp)
