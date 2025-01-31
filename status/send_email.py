"""Module for sending email notifications related to CrawJUD-Bots executions."""

from os import environ

from dotenv_vault import load_dotenv
from flask import Flask
from flask_mail import Mail, Message

load_dotenv()


def email_start(execution: None, app: Flask) -> None:
    """
    Send an email notification when an execution starts.

    Args:
        execution (Executions): The execution instance that has started.
        app (Flask): The Flask application instance.

    Raises:
        Exception: If an error occurs while sending the email.
    """
    from app.models import Executions, Users

    execution: Executions = execution

    mail = Mail(app)

    with app.app_context():
        mail.connect()

    admins: list[str] = []
    pid = execution.pid
    usr: Users = execution.user
    url_web = environ.get("url_web")

    display_name = execution.bot.display_name
    xlsx = execution.arquivo_xlsx

    try:
        for adm in usr.licenseusr.admins:
            admins.append(adm.email)

    except Exception as e:
        print(e)

    with app.app_context():
        url_web = environ.get("url_web")
        sendermail = environ["MAIL_DEFAULT_SENDER"]

        robot = f"Robot Notifications <{sendermail}>"
        assunto = "Initialization Notification"
        destinatario = usr.email
        mensagem = f"""<h1>Initialization Notification - PID {pid}</h1>
                      <p>Hello {usr.nome_usuario}, your execution has started successfully!</p>
                      <ul>
                          <li>Robot: {display_name}</li>
                          <li>Spreadsheet: {xlsx}</li>
                      </ul>
                      <p>Monitor the robot's execution in <b><a href="{url_web}/logs_bot/{pid}">Our System</a></b></p>
                      <p>Please, <b>DO NOT REPLY TO THIS EMAIL</b></p>
        """

        msg = Message(assunto, sender=robot, recipients=[destinatario], html=mensagem)
        if usr.email not in admins:
            msg = Message(
                assunto,
                sender=robot,
                recipients=[destinatario],
                html=mensagem,
                cc=admins,
            )

        mail.send(msg)


def email_stop(execution: None, app: Flask) -> None:
    """
    Send an email notification when an execution stops.

    Args:
        execution (Executions): The execution instance that has stopped.
        app (Flask): The Flask application instance.

    Raises:
        Exception: If an error occurs while sending the email.
    """
    from app.models import Executions, Users

    execution: Executions = execution

    mail = app.extensions.get("mail")
    if not mail:
        mail = Mail(app)

    with app.app_context():
        mail.connect()

    admins: list[str] = []
    pid = execution.pid
    usr: Users = execution.user
    url_web = environ.get("url_web")

    display_name = execution.bot.display_name
    xlsx = execution.arquivo_xlsx

    try:
        for adm in usr.licenseusr.admins:
            admins.append(adm.email)

    except Exception as e:
        print(e)

    with app.app_context():
        url_web = environ.get("url_web")
        sendermail = environ["MAIL_DEFAULT_SENDER"]

        robot = f"Robot Notifications <{sendermail}>"
        assunto = "Completion Notification"
        destinatario = usr.email
        mensagem = f"""<h1>Completion Notification - PID {pid}</h1>
                      <p>Hello {usr.nome_usuario}, your execution has been completed!</p>
                      <ul>
                          <li>Robot: {display_name}</li>
                          <li>Spreadsheet: {xlsx}</li>
                      </ul>
                      <p>Check the execution status in <b><a href="{url_web}/logs_bot/{pid}">Our System</a></b></p>
                      <p>Please, <b>DO NOT REPLY TO THIS EMAIL</b></p>
        """

        msg = Message(assunto, sender=robot, recipients=[destinatario], html=mensagem)
        if usr.email not in admins:
            msg = Message(
                assunto,
                sender=robot,
                recipients=[destinatario],
                html=mensagem,
                cc=admins,
            )

        mail.send(msg)
