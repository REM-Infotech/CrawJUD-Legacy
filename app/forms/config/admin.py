"""Module for admin user forms with validations and dynamic choices for licensing and user types."""

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from ..validators import NotSelecioneValidator


class UserForm(FlaskForm):
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

    def __init__(self, licenses_add: list = None, *args, **kwargs) -> None:
        """Initialize the user form with optional licensing choices.

        Args:
            licenses_add (list, optional): A list of license objects to add. Defaults to None.

        """
        super().__init__(*args, **kwargs)

        if licenses_add:
            licenses = []
            for lcs in licenses_add:
                licenses.append((str(lcs.license_token), str(lcs.name_client)))

            self.tipo_user.choices.extend([("supersu", "Super Administrador")])
            self.licenses.choices.extend(licenses)

        elif licenses_add is None:
            del self.licenses


class UserFormEdit(FlaskForm):
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

    def __init__(self, licenses_add: list = None, *args, **kwargs) -> None:
        """Initialize the edit form with optional licensing choices.

        Args:
            licenses_add (list, optional): A list of license objects to add. Defaults to None.

        """
        super().__init__(*args, **kwargs)

        if licenses_add:
            licenses = []
            for lcs in licenses_add:
                licenses.append((str(lcs.license_token), str(lcs.name_client)))

            self.tipo_user.choices.extend([("supersu", "Super Administrador")])
            self.licenses.choices.extend(licenses)

        elif licenses_add is None:
            del self.licenses
