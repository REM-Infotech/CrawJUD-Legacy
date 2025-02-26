"""Module for admin user forms with validations and dynamic choices for licensing and user types."""

from typing import Type

from quart_wtf import QuartForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from crawjud_bots.web.types import AnyType, T

from ...validators import NotSelecioneValidator


class UserForm(QuartForm):
    """Form for creating a user with license selection and user type management."""

    nome_usuario = StringField(label="Nome", validators=[DataRequired()])
    login = StringField(label="Login", validators=[DataRequired()])
    email = StringField(label="Email", validators=[DataRequired()])
    password = PasswordField(label="Senha", validators=[DataRequired(), Length(min=8, max=62)])
    show_password = BooleanField("Exibir senha", id="check")
    tipo_user = SelectField(
        label="Tipo de usuário",
        choices=[
            ("Selecione", "Selecione"),
            ("default_user", "Usuário Padrão"),
            ("admin", "Administrador"),
        ],
        validators=[
            DataRequired(message="Você deve selecionar um tipo de usuário."),
            NotSelecioneValidator(message="Você deve selecionar um tipo de usuário."),
        ],
    )

    licenses = SelectField(
        label="Selecione a Licença",
        choices=[("", "Selecione")],
        validators=[
            DataRequired(message="Você deve selecionar uma licença."),
            NotSelecioneValidator(message="Você deve selecionar uma licença."),
        ],
    )
    submit = SubmitField(label="Salvar Alterações")

    @classmethod
    async def create_form2(
        cls: Type[T],
        *args: AnyType,
        **kwargs: Type[AnyType],
    ) -> T:
        """Create a form instance."""
        self: UserForm = await cls.create_form(
            *args,
            **kwargs,
        )
        licenses_add = kwargs.get("licenses")
        if licenses_add:
            licenses = []
            for lcs in licenses_add:
                licenses.append((str(lcs.license_token), str(lcs.name_client)))

            self.tipo_user.choices.extend([("supersu", "Super Administrador")])
            self.licenses.choices.extend(licenses)

        elif licenses_add is None:
            del self.licenses

        return self


class UserFormEdit(QuartForm):
    """Form for editing user details with dynamic licensing options."""

    nome_usuario = StringField(label="Nome", validators=[DataRequired()])
    login = StringField(label="Login", validators=[DataRequired()])
    email = StringField(label="Email", validators=[DataRequired()])
    password = PasswordField(label="Senha")
    show_password = BooleanField("Exibir senha", id="check")
    tipo_user = SelectField(
        label="Tipo de usuário",
        choices=[
            ("Selecione", "Selecione"),
            ("default_user", "Usuário Padrão"),
            ("admin", "Administrador"),
        ],
    )

    licenses = SelectField(
        label="Selecione a Licença",
        choices=[("", "Selecione")],
    )
    submit = SubmitField(label="Salvar Alterações")

    @classmethod
    async def create_form2(
        cls: Type[T],
        *args: AnyType,
        **kwargs: Type[AnyType],
    ) -> T:
        """Create a form instance."""
        self: UserFormEdit = await cls.create_form(
            *args,
            **kwargs,
        )

        licenses_add = kwargs.get("licenses")

        if licenses_add:
            licenses = []
            for lcs in licenses_add:
                licenses.append((str(lcs.license_token), str(lcs.name_client)))

            self.tipo_user.choices.extend([("supersu", "Super Administrador")])
            self.licenses.choices.extend(licenses)

        elif licenses_add is None:
            del self.licenses

        return self
