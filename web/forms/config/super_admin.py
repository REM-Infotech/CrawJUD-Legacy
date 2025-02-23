"""Module for super_admin form configurations."""

from wtforms import SelectField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired


class ClienteForm:
    """Form for creating a client."""

    name_client = StringField(label="Nome do Cliente", validators=[DataRequired()])
    cpf_cnpj = StringField(label="CPF/CNPJ", validators=[DataRequired()])
    submit = SubmitField(label="Salvar Alterações")


class BotLicenseAssociationForm:
    """Form for associating bots with a license."""

    bot = SelectMultipleField(label="Bots", validators=[DataRequired()], choices=[("", "Selecione")])
    license_client = SelectField(label="Cliente", validators=[DataRequired()], choices=[("", "Selecione")])
    submit = SubmitField(label="Salvar Alterações")
