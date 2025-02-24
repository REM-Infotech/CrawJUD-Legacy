"""Flask-Login for Quart."""

from functools import wraps
from typing import Any, Callable, TypeVar

import quart_flask_patch  # noqa: F401
from flask_login import LoginManager
from flask_login.config import (
    AUTH_HEADER_NAME,  # noqa: F401
    COOKIE_DURATION,  # noqa: F401
    COOKIE_HTTPONLY,  # noqa: F401
    COOKIE_NAME,  # noqa: F401
    COOKIE_SAMESITE,  # noqa: F401
    COOKIE_SECURE,  # noqa: F401
    EXEMPT_METHODS,
    ID_ATTRIBUTE,  # noqa: F401
    LOGIN_MESSAGE,  # noqa: F401
    LOGIN_MESSAGE_CATEGORY,  # noqa: F401
    REFRESH_MESSAGE,  # noqa: F401
    REFRESH_MESSAGE_CATEGORY,  # noqa: F401
    SESSION_KEYS,  # noqa: F401
    USE_SESSION_FOR_NEXT,
)
from flask_login.mixins import AnonymousUserMixin  # noqa: F401
from flask_login.signals import (
    session_protected,  # noqa: F401
    user_accessed,  # noqa: F401
    user_loaded_from_cookie,  # noqa: F401
    user_loaded_from_request,  # noqa: F401
    user_needs_refresh,  # noqa: F401
    user_unauthorized,
)
from flask_login.utils import (
    _create_identifier,  # noqa: F401
    _user_context_processor,  # noqa: F401
    decode_cookie,  # noqa: F401
    encode_cookie,  # noqa: F401
    expand_login_view,
    make_next_param,
)
from flask_login.utils import login_url as make_login_url
from quart import (
    Request,
    abort,
    current_app,
    flash,
    g,
    has_request_context,
    make_response,  # noqa: F401
    redirect,
    request,
    session,
    url_for,  # noqa: F401
)
from werkzeug.local import LocalProxy

current_user = LocalProxy(lambda: _get_user())
AnyType = TypeVar("AnyType", str, bytes, Any, Request)
WrappedFnReturnT = TypeVar("WrappedFnReturnT")


def _get_user() -> AnyType:
    if has_request_context():
        if "_login_user" not in g:
            current_app.login_manager._load_user()  # noqa: SLF001

        return g._login_user  # noqa: SLF001

    return None


class QuartLoginManager(LoginManager):
    """Flask-Login for Quart."""

    async def unauthorized(self) -> AnyType:
        """Redirect a user to the login page.

        This is called when the user is required to log in. If you register a
        callback with :meth:`LoginManager.unauthorized_handler`, then it will
        be called. Otherwise, it will take the following actions:

            - Flash :attr:`LoginManager.login_message` to the user.

            - If the app is using blueprints find the login view for
              the current blueprint using `blueprint_login_views`. If the app
              is not using blueprints or the login view for the current
              blueprint is not specified use the value of `login_view`.

            - Redirect the user to the login view. (The page they were
              attempting to access will be passed in the ``next`` query
              string variable, so you can redirect there if present instead
              of the homepage. Alternatively, it will be added to the session
              as ``next`` if USE_SESSION_FOR_NEXT is set.)

        If :attr:`LoginManager.login_view` is not defined, then it will simply
        raise a HTTP 401 (Unauthorized) error instead.

        This should be returned from a view or before/after_request function,
        otherwise the redirect will have no effect.
        """
        user_unauthorized.send(
            current_app._get_current_object()  # noqa: SLF001
        )

        if self.unauthorized_callback:
            return self.unauthorized_callback()

        if request.blueprint in self.blueprint_login_views:
            login_view = self.blueprint_login_views[request.blueprint]
        else:
            login_view = self.login_view

        if not login_view:
            abort(401)

        if self.login_message:
            if self.localize_callback is not None:
                await flash(
                    self.localize_callback(self.login_message),
                    category=self.login_message_category,
                )
            else:
                await flash(self.login_message, category=self.login_message_category)

        config = current_app.config
        if config.get("USE_SESSION_FOR_NEXT", USE_SESSION_FOR_NEXT):
            login_url = expand_login_view(login_view)
            session["_id"] = self._session_identifier_generator()
            session["next"] = make_next_param(login_url, request.url)
            redirect_url = make_login_url(login_view)
        else:
            redirect_url = make_login_url(login_view, next_url=request.url)

        return redirect(redirect_url)


def login_required(func: Callable[[], AnyType]) -> WrappedFnReturnT:
    """Protect views requiring authentication.

    If you decorate a view with this, it will ensure that the current user is
        logged in and authenticated before calling the actual view. (If they are
        not, it calls the :attr:`LoginManager.unauthorized` callback.).

    Example:
        @app.route("/post")
        @login_required
        def post():
            pass

    If there are only certain times you need to require that your user is
    logged in, you can do so with::

        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()

    ...which is essentially the code that this function adds to your views.

    It can be convenient to globally turn off authentication when unit testing.
    To enable this, if the application configuration variable `LOGIN_DISABLED`
    is set to `True`, this decorator will be ignored.

    .. Note ::

        Per `W3 guidelines for CORS preflight requests
        <http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0>`_,
        HTTP ``OPTIONS`` requests are exempt from login checks.

    :param func: The view function to decorate.
    :type func: function

    """

    @wraps(func)
    async def decorated_view(*args: AnyType, **kwargs: AnyType) -> AnyType:
        if request.method in EXEMPT_METHODS or current_app.config.get("LOGIN_DISABLED"):
            pass
        elif has_request_context():
            if not current_user.is_authenticated:
                return await current_app.login_manager.unauthorized()

        # flask 1.x compatibility
        # current_app.ensure_sync is only available in Flask >= 2.0
        if callable(getattr(current_app, "ensure_sync", None)):
            return current_app.ensure_sync(func)(*args, **kwargs)
        return func(*args, **kwargs)

    return decorated_view
