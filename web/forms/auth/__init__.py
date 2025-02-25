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

    def __init__(
        self,
        *args: AnyType,
        **kwargs: AnyType,
    ) -> None:
        """Initialize the form."""
        super().__init__(
            *args,
            **kwargs,
        )

    @classmethod
    async def create_form(
        cls: Type[T],
        formdata: AnyType = ...,
        obj: AnyType = None,
        prefix: AnyType = "",
        data: AnyType = None,
        meta: AnyType = None,
        **kwargs: AnyType,
    ) -> T:
        """Create a form instance."""
        return await super().create_form(
            formdata,
            obj,
            prefix,
            data,
            meta,
            **kwargs,
        )
