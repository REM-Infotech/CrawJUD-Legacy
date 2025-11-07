"""Module for credential forms handling certificate and password authentication."""

from typing import Type

from flask_wtf.file import FileAllowed, FileField
from quart_wtf import QuartForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired

from crawjud.types import AnyType, T

file_allowed = FileAllowed(["pfx", 'Apenas arquivos ".pfx" são permitidos!'])


class CredentialsForm(QuartForm):
    """Form for handling credentials including certificate and login/password methods."""

    nome_cred = StringField("Nome da credencial", validators=[DataRequired("Informe o nome de referência!")])

    system = SelectField("Selecione o sistema", choices=[("Selecione", "Selecione")])

    auth_method = SelectField(
        "Selecione o método de login",
        id="auth_method",
        choices=[
            ("Selecione", "Selecione"),
            ("cert", "Certificado"),
            ("pw", "Login/Senha"),
        ],
    )

    login = StringField("Usuário")
    password = PasswordField("Senha")

    doc_cert = StringField("CPF/CNPJ do Certificado")
    cert = FileField(
        "Selecione o certificado",
        validators=[file_allowed],
        render_kw={"accept": ".pfx"},
    )
    key = PasswordField("Informe a senha do certificado")

    submit = SubmitField("Salvar")

    @classmethod
    async def setup_form(
        cls: Type[T],
        *args: AnyType,
        **kwargs: Type[AnyType],
    ) -> T:
        """Create a form instance."""
        self: CredentialsForm = await cls.create_form(
            *args,
            **kwargs,
        )

        systems = kwargs.get("system")
        if systems:
            self.system.choices.extend(systems)

        return self
