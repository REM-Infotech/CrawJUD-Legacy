"""Module for server-related models."""

from web import db


class Servers(db.Model):
    """Database model for servers."""

    __tablename__ = "servers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=45), nullable=False)
    address = db.Column(db.String(length=45), nullable=False)
    system = db.Column(db.String(length=45), nullable=False)
