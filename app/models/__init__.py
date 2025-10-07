"""Models para o aplicativo."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.models.admin.license import License

from .admin import User

__all__ = ["User"]


def init_database(app: Flask) -> None:
    """Inicializa o banco de dados."""
    with app.app_context():
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        db.create_all()


def create_default_admin(app: Flask) -> None:
    """Cria um usuário admin padrão se não existir."""
    with app.app_context():
        db: SQLAlchemy = app.extensions["sqlalchemy"]

        users = User.query.filter_by(UserName="admin").all()
        if not users:
            licenses = License.query.all()

            license_ = License(
                Id=len(licenses),
                Name="Licença Administrador",
                Description="Licença com acesso a todos os robôs",
            )

            admin = User(
                Id=len(users),
                UserName="admin",
                DisplayName="Administrator",
                Email="admin@robotz.dev",
                License=license_,
                license_id=license_.Id,
            )

            db.session.add_all([admin, license_])
            db.session.commit()
