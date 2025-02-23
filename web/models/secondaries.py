"""Module defining secondary association tables for many-to-many relationships."""

from web import db

admins = db.Table(
    "admins",
    db.Column("users_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("license_user_id", db.Integer, db.ForeignKey("licenses_users.id")),
)


execution_bots = db.Table(
    "execution_bots",
    db.Column("bot_id", db.Integer, db.ForeignKey("bots.id")),
    db.Column("licenses_users_id", db.Integer, db.ForeignKey("licenses_users.id")),
)
