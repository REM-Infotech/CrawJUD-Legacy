"""Database model for servers in CrawJUD-Bots."""

from app import db


class Servers(db.Model):
    """Represents a server with its configuration details."""

    __tablename__ = "servers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=45), nullable=False)
    address = db.Column(db.String(length=45), nullable=False)
    system = db.Column(db.String(length=45), nullable=False)
