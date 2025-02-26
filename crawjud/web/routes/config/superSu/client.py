"""Module for Super Su client route functionality."""

from quart import Response, abort, make_response, render_template

from crawjud.decorators import check_privilegies, login_required

from . import supersu


@supersu.route("/cadastro/cliente", methods=["GET", "POST"])
@login_required
@check_privilegies
async def cadastro_cliente() -> Response:
    """Render the client registration template.

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


@supersu.route("/editar/cliente", methods=["GET", "POST"])
@login_required
@check_privilegies
async def edit_cliente() -> Response:
    """Render the client edit template.

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
