"""Module for authentication forms."""

from typing import Type

from quart_wtf import QuartForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired

from web.types import AnyType, T


class LoginForm(QuartForm):
    """Form for user login with required credentials."""

    login = StringField("Usuário", validators=[DataRequired("Informe o usuário!")])
    password = PasswordField("Senha", validators=[DataRequired("Informe a Senha!")])
    remember_me = BooleanField("Manter sessão")
    submit = SubmitField("Entrar")

    @classmethod
    async def create_form2(
        cls: Type[T],
        formdata: Type[AnyType] = ...,
        obj: Type[AnyType] = None,
        prefix: Type[AnyType] = "",
        data: Type[AnyType] = None,
        meta: Type[AnyType] = None,
        **kwargs: Type[AnyType],
    ) -> T:
        """Create a form instance."""
        return await cls.create_form(
            formdata,
            obj,
            prefix,
            data,
            meta,
            **kwargs,
        )
