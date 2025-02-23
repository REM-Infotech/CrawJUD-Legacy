"""Module for Super Su client route functionality."""

from flask import Response, abort, make_response, render_template
from flask_login import login_required

from ....decorators import check_privilegies
from . import supersu


@supersu.route("/cadastro/cliente", methods=["GET", "POST"])
@login_required
@check_privilegies
def cadastro_bot() -> Response:
    """Render the client registration template.

    Returns:
        str: Rendered HTML template.

    """
    try:
        return make_response(render_template("index.html"))

    except Exception as e:
        abort(500, description=f"Erro interno do servidor: {e!s}")


@supersu.route("/editar/cliente", methods=["GET", "POST"])
@login_required
@check_privilegies
def licencas_associadas() -> Response:
    """Render the client edit template.

    Returns:
        str: Rendered HTML template.

    """
    try:
        return make_response(render_template("index.html"))

    except Exception as e:
        abort(500, description=f"Erro interno do servidor: {e!s}")
