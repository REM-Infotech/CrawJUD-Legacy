"""Module for user configuration routes.

This module provides endpoints for user-specific profile configuration settings.
"""

import os
import pathlib

from flask import Blueprint, Response, make_response, render_template
from flask_login import login_required

path_template = os.path.join(pathlib.Path(__file__).parent.resolve(), "templates")
usr = Blueprint("usr", __name__, template_folder=path_template)


@usr.route("/profile_config", methods=["GET", "POST"])
@login_required
def profile_config() -> Response:
    """Render the user profile configuration page.

    Returns:
        Response: A Flask response rendering the profile configuration.

    """
    pagina = "config_page.html"
    return make_response(render_template("index.html", pagina=pagina))
