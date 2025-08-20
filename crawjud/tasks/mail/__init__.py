"""Gerencie o envio de e-mails automatizados para diferentes tipos de notificação.

Este módulo fornece funcionalidades para compor e enviar e-mails utilizando
templates e variáveis de ambiente para configuração do servidor SMTP.

"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import dotenv_values
from flask_mail import Message
from jinja2 import Environment, FileSystemLoader

from crawjud.api import create_app
from crawjud.decorators import shared_task

environ = dotenv_values()

if TYPE_CHECKING:
    from flask_mail import Mail

path_templates = str(Path(__file__).parent.joinpath("templates"))
environment = Environment(
    loader=FileSystemLoader(path_templates),
    autoescape=True,
)


@shared_task(name="send_email")
async def send_email(
    bot_name: str,
    pid: str,
    nome_planilha: str,
    user_name: str,
    email_target: str,
    email_type: str = "start",
    cc: list[str] | None = None,
) -> None:
    """Envia um e-mail utilizando as configurações do servidor SMTP."""
    app = await create_app()

    async with app.app_context():
        mail: Mail = app.extensions["mail"]

        message = Message()

        url_web = environ["URL_WEB"]
        default_sender = environ["MAIL_DEFAULT_SENDER"]
        message.subject = f"Notificação Robô <{default_sender}>"
        message.cc = cc
        message.recipients = [email_target]

        template = environment.get_template(f"email_{email_type}.jinja")
        message.html = template.render(
            username=user_name,
            display_name=bot_name,
            url_web=url_web,
            pid=pid,
            xlsx=nome_planilha,
        )

        mail.send(message=message)
