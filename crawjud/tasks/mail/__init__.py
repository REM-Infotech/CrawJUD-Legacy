"""Gerencie o envio de e-mails automatizados para diferentes tipos de notificação.

Este módulo fornece funcionalidades para compor e enviar e-mails utilizando
templates e variáveis de ambiente para configuração do servidor SMTP.

"""

from __future__ import annotations

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from smtplib import SMTP

from dotenv import dotenv_values
from jinja2 import Environment, FileSystemLoader

from crawjud.decorators import shared_task

environ = dotenv_values()

path_templates = str(Path(__file__).parent.joinpath("templates"))
environment_ = Environment(
    loader=FileSystemLoader(path_templates),
    autoescape=True,
)


@shared_task("send_email")
def send_email(
    bot_name: str,
    user_name: str,
    email_target: str,
    email_type: str = "start",
    cc: list[str] | None = None,
) -> None:
    """Envia um e-mail utilizando as configurações do servidor SMTP."""
    server = environ["MAIL_SERVER"]
    port = environ["MAIL_PORT"]
    use_tls = environ["MAIL_USE_TLS"].lower() == "true"
    _use_ssl = environ["MAIL_USE_SSL"].lower() == "true"
    username = environ["MAIL_USERNAME"]
    password = environ["MAIL_PASSWORD"]
    default_sender = environ["MAIL_DEFAULT_SENDER"]

    with SMTP(server, port) as smtp:
        smtp.ehlo()
        if use_tls:
            smtp.starttls()
        smtp.login(username, password)

        msg = MIMEMultipart()
        msg["From"] = default_sender
        msg["To"] = email_target
        msg["Subject"] = email_type
        msg["cc"] = ", ".join(cc) if cc else ""

        body = f"Hello {user_name},\n\nThis is a {email_type} email from {bot_name}."
        msg.attach(MIMEText(body, "plain"))

        smtp.sendmail(
            from_addr=default_sender,
            to_addrs=email_target,
            msg=msg.as_string(),
        )
