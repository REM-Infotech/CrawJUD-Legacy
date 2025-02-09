"""Module for bot execution forms and associated helper functions for file uploads and dynamic choices."""

import json
import os
import pathlib
from datetime import datetime

import pytz
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, MultipleFileField
from wtforms import (
    BooleanField,
    DateField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, InputRequired

permited_file = FileAllowed(["xlsx", "xls", "csv"], 'Apenas arquivos |".xlsx"/".xls"/".csv"| são permitidos!')
permited_file2 = FileAllowed(["pdf", "jpg", "jpeg"], 'Apenas arquivos |".pdf"/".jpg"/".jpeg"| são permitidos!')


class BotForm(FlaskForm):
    """Form to configure and execute bot tasks with file uploads and dynamic selections."""

    xlsx = FileField(
        "Arquivo de execução",
        validators=[permited_file],
        render_kw={"accept": ".xlsx, .xls, .csv"},
    )

    parte_name = StringField("Nome da parte")
    doc_parte = StringField("CPF/CNPJ da parte")
    polo_parte = SelectField(
        "Classificação (Autor/Réu)",
        choices=[("", "Selecione"), ("autor", "Autor"), ("reu", "Réu")],
        validators=[DataRequired(message="Você deve selecionar uma classificação.")],
    )

    data_inicio = DateField("Data de Início", default=datetime.now(pytz.timezone("Etc/GMT+4")))
    data_fim = DateField("Data Fim", default=datetime.now(pytz.timezone("Etc/GMT+4")))

    otherfiles = MultipleFileField(
        "Arquivo adicionais",
        validators=[permited_file2],
        render_kw={"accept": ".pdf, .jpg, .jpeg"},
    )

    creds = SelectField(
        "Selecione a Credencial",
        choices=[("", "Selecione")],
        validators=[DataRequired(message="Você deve selecionar uma credencial.")],
    )
    password = StringField("Senha token")
    state = SelectField(
        "Selecione o Estado",
        choices=[("", "Selecione")],
        validators=[DataRequired(message="Você deve selecionar um estado.")],
    )
    varas = SelectMultipleField(
        "Selecione a Vara",
        choices=[("", "Selecione")],
        validators=[DataRequired(message="Você deve selecionar uma vara.")],
    )
    client = SelectField(
        "Selecione o Cliente",
        choices=[("", "Selecione")],
        validators=[DataRequired(message="Você deve selecionar um cliente.")],
    )

    confirm_fields = BooleanField(
        "Confirmo que os dados enviados estão corretos.",
        validators=[InputRequired(message="Você deve confirmar que os dados estão corretos.")],
    )

    submit = SubmitField("Iniciar Execução")

    def __init__(self, *args, dynamic_fields=None, **kwargs):
        """Initialize the BotForm with dynamic field validation and choice population.

        Args:
            dynamic_fields (list, optional): List of fields to retain. Defaults to None.

        """
        super(BotForm, self).__init__(*args, **kwargs)

        # Remover os campos que não estão na lista de fields dinâmicos
        if dynamic_fields:
            # Remover campos que não estão na lista
            for field_name in list(self._fields.keys()):
                if field_name not in dynamic_fields:
                    del self._fields[field_name]

        if kwargs.get("system"):
            choices = []
            all_varas = varas().get(kwargs["system"].upper())
            if all_varas:
                for estado, juizados in all_varas.items():
                    for juizado, comarcas in juizados.items():
                        for comarca_key, comarca_value in comarcas.items():
                            choices.append((
                                comarca_value,
                                comarca_key,
                                {
                                    "data-juizado": f"{len(choices)}_{juizado}",
                                    "data-juizado_estado": f"{estado}",
                                },
                            ))

        self.varas.choices.extend(choices)
        # Se tiver 'state' e 'creds' no kwargs, popular as escolhas
        if kwargs.get("state"):
            self.state.choices.extend(kwargs.get("state"))

        if kwargs.get("clients"):
            self.client.choices.extend(kwargs.get("clients"))

        if kwargs.get("creds"):
            self.creds.choices.extend(kwargs.get("creds"))


class SearchExec(FlaskForm):
    """Form to search within bot executions by execution field."""

    campo_busca = StringField("Buscar Execução")
    submit = SubmitField("Buscar")


def varas() -> dict[str, dict[str, dict[str, dict[str, str]]]]:
    """Load and return a dictionary of varas data from a JSON file.

    Returns:
        dict[str, dict[str, dict[str, dict[str, str]]]]: Nested dictionary of varas.

    """
    file_p = pathlib.Path(__file__).parent.resolve()
    file_json = os.path.join(file_p, "varas.json")

    dict_files = {}

    with open(file_json, "rb") as f:
        obj = f.read()
        dict_files = json.loads(obj)

    return dict_files


class AddBot(FlaskForm):
    """Form to add a new bot configuration with various selection options."""

    display_name = StringField("Nome do Robô")
    system = SelectField("Sistema", choices=[("TJ", "TJ")])
    state = SelectField("Estado", choices=[])
    client = SelectField("Cliente", choices=[])
    type = SelectField("Tipo", choices=[])
    form_cfg = SelectField("Configuração", choices=[])
    classification = SelectField("Classificação", choices=[])
    text = StringField("Texto")
    submit = SubmitField("Adicionar Robô")
