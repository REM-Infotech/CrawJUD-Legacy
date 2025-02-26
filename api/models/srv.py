"""Defines the Servers model for the CrawJUD-Bots application.

This model stores server configuration details such as name, address, and system type.
"""

from api import db


class Servers(db.Model):
    """Represents a server configuration.

    Attributes:
        id (int): Primary key for the server entry.
        name (str): Name of the server.
        address (str): IP address or hostname of the server.
        system (str): System type or identifier for the server.

    """

    __tablename__ = "servers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=45), nullable=False)
    address = db.Column(db.String(length=45), nullable=False)
    system = db.Column(db.String(length=45), nullable=False)
