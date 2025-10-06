from __future__ import annotations

from typing import TYPE_CHECKING

from flask_sqlalchemy import SQLAlchemy

if TYPE_CHECKING:
    from flask import Flask


db = SQLAlchemy()


def start_extensions(app: Flask) -> None:
    db.init_app(app)

    from app import models

    _ = models
