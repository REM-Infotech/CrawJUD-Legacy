"""Models para o aplicativo."""

from flask import Flask

from .admin import User

__all__ = ["User"]


def init_database(app: Flask) -> None:
    """Inicializa o banco de dados."""
    with app.app_context():
        from app.resources.extensions import db

        db.create_all()


def create_default_admin(app: Flask) -> None:
    """Cria um usuário admin padrão se não existir."""
    from app.models.admin.user import User
    from app.resources.extensions import db

    with app.app_context():
        if not db.session.query(User).filter_by(username="admin").first():
            _admin = User()
