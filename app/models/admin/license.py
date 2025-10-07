from sqlalchemy import Column, Integer, String

from app.config.extensions import db


class License(db.Model):
    __tablename__ = "licenses"
    Id = Column("id", Integer, primary_key=True, nullable=False, unique=True)
    Name = Column("name", String(128), nullable=False)
    Description = Column("description", String(256), nullable=False)
