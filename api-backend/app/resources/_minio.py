from collections.abc import Callable
from functools import wraps

from dotenv import load_dotenv
from flask import Flask
from minio import Minio as MinioClient
from minio.credentials.providers import EnvMinioProvider

from __types import P

load_dotenv()


class Minio(MinioClient):
    flask_app: Flask

    def __init__(
        self,
        app: Flask | None = None,
    ) -> None:
        if app:
            with app.app_context():
                super().__init__(
                    endpoint=app.config["MINIO_ENDPOINT"],
                    access_key=app.config.get("MINIO_ACCESS_KEY", None),
                    secret_key=app.config.get("MINIO_SECRET_KEY", None),
                    session_token=app.config.get(
                        "MINIO_SESSION_TOKEN", None
                    ),
                    secure=app.config.get("MINIO_SECURE", True),
                    region=app.config.get("MINIO_REGION", None),
                    http_client=app.config.get(
                        "MINIO_HTTP_CLIENT", None
                    ),
                    credentials=app.config.get(
                        "MINIO_CREDENTIALS", None
                    ),
                    cert_check=app.config.get("MINIO_CERT_CHECK", True),
                )
                self.flask_app = app
                app.extensions["storage"] = self
                self.decorate_functions()

    def init_app(self, app: Flask) -> None:
        """Inicializa a extensão com a aplicação Flask."""
        if app.extensions.get("storage"):
            return

        with app.app_context():
            super().__init__(
                endpoint=app.config["MINIO_ENDPOINT"],
                access_key=app.config.get("MINIO_ACCESS_KEY", None),
                secret_key=app.config.get("MINIO_SECRET_KEY", None),
                session_token=app.config.get(
                    "MINIO_SESSION_TOKEN", None
                ),
                secure=app.config.get("MINIO_SECURE", False),
                region=app.config.get("MINIO_REGION", None),
                http_client=app.config.get("MINIO_HTTP_CLIENT", None),
                credentials=EnvMinioProvider(),
                cert_check=app.config.get("MINIO_CERT_CHECK", False),
            )

            self.flask_app = app
            app.extensions["storage"] = self
            self.decorate_functions()

    def decorate_functions(self) -> None:
        for item in dir(self):
            if (
                not item.startswith("_")
                and item != "init_app"
                and callable(getattr(self, item))
            ):
                setattr(self, item, self.wrapper(getattr(self, item)))

    def wrapper[T](self, func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapped_function(*args: P.args, **kwargs: P.kwargs) -> T:
            return func(*args, **kwargs)

        return wrapped_function
