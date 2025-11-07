import traceback
from typing import ClassVar, Self

from flask_jwt_extended import get_current_user
from tqdm import tqdm

from app.models import LicenseUser, User, db
from app.resources import camel_to_snake
from app.types import Dict


class FormBot:
    _subclass: ClassVar[dict[str, type[Self]]] = {}

    @classmethod
    def load_form(cls, form_name: str, kwargs: Dict) -> Self:
        return cls._subclass[form_name.replace("_", "")](**kwargs)

    def handle_task(self, pid_exec: str) -> None:
        try:
            from app.models import Bots
            from app.resources.extensions import celery, db

            kwargs = self.to_dict()
            kwargs["pid"] = pid_exec
            bot = db.session.query(Bots).filter(Bots.Id == self.bot_id).first()

            kwargs["sistema"] = bot.sistema.lower()
            kwargs["categoria"] = bot.categoria.lower()

            celery.send_task("crawjud", kwargs={"config": kwargs})

        except Exception as e:
            exc = "\n".join(traceback.format_exception(e))
            tqdm.write(exc)

    def to_dict(self) -> Dict:
        data = {}

        keys = list(
            filter(
                lambda key: not key.startswith("_")
                and not callable(getattr(self, key, None)),
                dir(self),
            ),
        )

        for key in keys:
            value = getattr(self, key)
            if key == "credencial":
                user: User = get_current_user()
                # Acessa 'credenciais' antes de fechar a sessão para evitar DetachedInstanceError
                lic = (
                    db.session.query(LicenseUser)
                    .select_from(User)
                    .join(LicenseUser.usuarios)
                    .filter(User.Id == user.Id)
                    .first()
                )

                credencial = list(
                    filter(
                        lambda x: x.Id == int(value),
                        lic.credenciais,
                    ),
                )[-1]

                data.update({
                    "credenciais": {
                        "username": credencial.login,
                        "password": credencial.password,
                    },
                })
                continue

            if key == "sid_filesocket":
                data.update({"folder_objeto_minio": value})
                continue

            data.update({key: value})

        return data

    def __init_subclass__(cls: type[Self]) -> None:
        cls._subclass[camel_to_snake(cls.__name__.lower())] = cls
