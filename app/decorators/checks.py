"""Module providing decorators and helper functions for access control."""

from functools import wraps
from typing import Any, Callable

from flask import Response, flash, make_response, redirect, session, url_for
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy

from ..models import Users


def check_su(func: Callable[..., Any]) -> Callable[..., Any]:
    """Check if the current user is a 'supersu'.

    Args:
        func (callable): The view function to wrap.

    Returns:
        callable: The wrapped function that checks user access.

    """

    @wraps(func)
    async def wrapper(*args: tuple, **kwargs: dict) -> Response:
        usuario: str = session["login"]
        if query_supersu(usuario) is False:
            flash("Acesso negado", "error")
            return await make_response(redirect(url_for("dash.dashboard")))
        return func(*args, **kwargs)

    return wrapper


def query_supersu(usuario: str) -> bool:
    """Query whether a given user is a 'supersu'.

    Args:
        usuario (str): The login identifier for the user.

    Returns:
        bool: True if user is a 'supersu', False otherwise.

    """
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    user = db.session.query(Users).filter(Users.login == usuario).first()

    if len(user.supersu) == 0:
        return False

    return True
