"""Module for super_admin form configurations."""

from typing import Type

from wtforms import SelectField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired

from crawjud.types import AnyType, T


class ClienteForm:
    """Form for creating a client."""

    name_client = StringField(label="Nome do Cliente", validators=[DataRequired()])
    cpf_cnpj = StringField(label="CPF/CNPJ", validators=[DataRequired()])
    submit = SubmitField(label="Salvar Alterações")

    @classmethod
    async def setup_form(
        cls: Type[T],
        formdata: AnyType = ...,
        obj: AnyType = None,
        prefix: AnyType = "",
        data: AnyType = None,
        meta: AnyType = None,
        **kwargs: AnyType,
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


class BotLicenseAssociationForm:
    """Form for associating bots with a license."""

    bot = SelectMultipleField(label="Bots", validators=[DataRequired()], choices=[("", "Selecione")])
    license_client = SelectField(label="Cliente", validators=[DataRequired()], choices=[("", "Selecione")])
    submit = SubmitField(label="Salvar Alterações")

    @classmethod
    async def setup_form(
        cls: Type[T],
        *args: AnyType,
        **kwargs: Type[AnyType],
    ) -> T:
        """Create a form instance."""
        return await cls.create_form(
            *args,
            **kwargs,
        )
