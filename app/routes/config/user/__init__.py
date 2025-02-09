"""Module for user configuration routes.

This module provides endpoints for user-specific profile configuration settings.
"""

from pathlib import Path

from flask_login import login_required
from quart import Blueprint, render_template

path_template = Path(__file__).parent.resolve().joinpath("templates")
usr = Blueprint("usr", __name__, template_folder=path_template)


@usr.route("/profile_config", methods=["GET", "POST"])
@login_required
async def profile_config():
    """Render the user profile configuration page.

    Returns:
        Response: A Quart response rendering the profile configuration.

    """
    pagina = "config_page.html"
    return render_template("index.html", pagina=pagina)
