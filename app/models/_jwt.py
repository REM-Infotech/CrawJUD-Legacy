"""Module for user-related models and authentication utilities."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import bcrypt
from flask_jwt_extended import get_current_user
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Mapped

from app.resources.extensions import db, jwt

from .users import Users

salt = bcrypt.gensalt()


@jwt.user_identity_loader
def user_identity_lookup[T](*args: T) -> int:
    """Get the user's identity.

    Returns:
        int: The user's ID.

    """
    user: Users = args[0]

    return user.id


@jwt.token_in_blacklist_loader
def check_if_token_revoked(
    jwt_data: dict,
    *args: str,
    **kwargs: object,
) -> bool:
    """Check if the token is in the blocklist.

    Returns:
        bool: True if the token is revoked, False otherwise.

    """
    jti = jwt_data["jti"] or kwargs.get("jti") or args[0].get("jti")
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None


@jwt.user_loader_callback_loader
def user_lookup_callback[T](*args: T) -> Users | None:
    """Get the user from the JWT data.

    Returns:
        Users | None: The user object or None if not found.

    """
    id_: int = args[0]

    return db.session.query(Users).filter_by(id=id_).one_or_none()


class TokenBlocklist(db.Model):
    """Database model for token blocklist."""

    id: int = Column(Integer, primary_key=True)
    jti: str = Column(String(36), nullable=False, index=True)
    type: str = Column(String(16), nullable=False)
    user_id = Column(
        db.ForeignKey("users.id"),
        default=lambda: get_current_user().id,
        nullable=False,
    )
    user: Mapped[Users] = db.relationship()
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(ZoneInfo("America/Manaus")),
        server_default=datetime.now(ZoneInfo("America/Manaus")).isoformat(),
        nullable=False,
    )
