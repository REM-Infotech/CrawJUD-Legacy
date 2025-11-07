"""Module for user-related models and authentication utilities."""

from __future__ import annotations

from contextlib import suppress
from datetime import datetime
from zoneinfo import ZoneInfo

import bcrypt
from flask_jwt_extended import get_current_user
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Mapped

from app.resources.extensions import db, jwt
from app.types import MyAny

from ._users import User

salt = bcrypt.gensalt()


@jwt.user_identity_loader
def user_identity_lookup(usr_id: int, *args: MyAny) -> int:
    """Get the user's identity.

    Returns:
        int: The user's ID.

    """
    return usr_id


@jwt.token_in_blocklist_loader
def check_if_token_revoked(
    *args: str,
    **kwargs: MyAny,
) -> bool:
    """Check if the token is in the blocklist.

    Returns:
        bool: True if the token is revoked, False otherwise.

    """
    jwt_data = {}
    for item in args:
        jwt_data.update(item)

    token = None
    with suppress(Exception):
        jti = jwt_data["jti"]
        token = db.session.query(TokenBlocklist.Id).filter_by(jti=jti).scalar()

    return token is not None


@jwt.user_lookup_loader
def user_lookup_callback(*args: MyAny, **kwargs: MyAny) -> User | None:
    """Get the user from the JWT data.

    Returns:
        User | None: The user object or None if not found.

    """
    jwt_data = {}
    for item in args:
        jwt_data.update(item)

    return (
        db.session.query(User).filter_by(Id=int(jwt_data["sub"])).one_or_none()
    )


class TokenBlocklist(db.Model):
    """Database model for token blocklist."""

    __tablename__ = "token_blocklist"
    Id: int = Column(Integer, primary_key=True)
    jti: str = Column(String(36), nullable=False, index=True)
    type: str = Column(String(16), nullable=False)
    user_id = Column(
        db.ForeignKey("users.id"),
        default=lambda: get_current_user().id,
        nullable=False,
    )
    user: Mapped[User] = db.relationship()
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(ZoneInfo("America/Manaus")),
        server_default=datetime.now(
            ZoneInfo("America/Manaus"),
        ).isoformat(),
        nullable=False,
    )
