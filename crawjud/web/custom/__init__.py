"""Flask-Login for Quart."""

from flask_login import LoginManager
from flask_login.config import (
    USE_SESSION_FOR_NEXT,
)
from flask_login.signals import (
    user_unauthorized,
)
from flask_login.utils import (
    expand_login_view,
    make_next_param,
)
from flask_login.utils import login_url as make_login_url
from quart import (
    abort,
    current_app,
    flash,
    redirect,
    request,
    session,
)

from crawjud.web.types import AnyType


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
