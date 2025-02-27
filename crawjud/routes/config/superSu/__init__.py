"""Module for Super Su configuration routes."""

import os
import pathlib
from importlib import import_module

from quart import Blueprint, Response, abort, make_response, render_template

from crawjud._decorators import check_privilegies, login_required

path_template = os.path.join(pathlib.Path(__file__).parent.resolve(), "templates")
supersu = Blueprint("supersu", __name__, template_folder=path_template)


@supersu.route("/configurações_crawjud", methods=["GET"])
@login_required
@check_privilegies
async def config() -> Response:
    """Render the configuration template for CrawJUD.

    Returns:
        str: Rendered HTML template.

    """
    try:
        return await make_response(
            await render_template(
                "index.html",
            ),
        )

    except Exception as e:
        abort(500, description=f"Erro interno do servidor: {e!s}")


def _other_routes() -> None:
    """Import other routes for the Super Su configuration blueprint."""
    import_module(".client", package=__package__)
    import_module(".bots", package=__package__)


_other_routes()
