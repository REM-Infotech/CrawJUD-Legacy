"""Module for form definitions used in the application.

Provides various FlaskForm subclasses.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SubmitField

from app.forms.auth.login import LoginForm
from app.forms.bot import BotForm, SearchExec
from app.forms.config import UserForm, UserFormEdit
from app.forms.credentials import CredentialsForm

__all__ = [LoginForm, BotForm, SearchExec, CredentialsForm, UserForm, UserFormEdit]


permited_file = FileAllowed(["xlsx", "xls"], 'Apenas arquivos ".xlsx" são permitidos!')


class IMPORTForm(FlaskForm):
    """Form for file importation.

    Attributes:
        arquivo: The file field accepting 'xlsx' or 'xls' files up to 50Mb.
        submit: The submission button for the form.

    """

    arquivo = FileField(
        label="Arquivo de importação. Máximo 50Mb",
        validators=[FileRequired(), permited_file],
    )
    submit = SubmitField(label="Importar")
