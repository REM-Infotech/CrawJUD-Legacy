"""Miscellaneous utilities and helpers for the CrawJUD-Bots application."""

import json
import random
import string
from datetime import datetime
from os import environ

import pytz
from dotenv_vault import load_dotenv
from flask import Flask
from google.cloud.storage import Bucket, Client
from google.cloud.storage.blob import Blob
from google.oauth2.service_account import Credentials

from git_py import _release_tag, check_latest, checkout_release, update_servers

signed_url_lifetime = 300
__all__ = [
    "GeoLoc",
    "_release_tag",
    "check_latest",
    "checkout_release",
    "update_servers",
    "init_log",
]

load_dotenv()


def generate_pid() -> str:
    """
    Generate a unique process identifier.

    Returns:
        str: A unique PID composed of interleaved letters and digits.
    """
    while True:
        # Gerar 4 letras maiúsculas e 4 dígitos
        letters = random.sample(string.ascii_uppercase, 6)
        digits = random.sample(string.digits, 6)

        # Intercalar letras e dígitos
        pid = "".join(
            [letters[i // 2] if i % 2 == 0 else digits[i // 2] for i in range(6)]
        )

        # Verificar se a string gerada não contém sequências do tipo "AABB"
        if not any(pid[i] == pid[i + 1] for i in range(len(pid) - 1)):
            return pid


def storageClient() -> Client:
    """
    Create a Google Cloud Storage client.

    Returns:
        Client: Configured GCS client.
    """
    project_id = environ.get("project_id")
    # Configure a autenticação para a conta de serviço do GCS
    credentials = CredentialsGCS()

    return Client(credentials=credentials, project=project_id)


def CredentialsGCS() -> Credentials:
    """
    Create Google Cloud Storage credentials from environment variables.

    Returns:
        Credentials: GCS service account credentials.
    """
    credentials_dict = json.loads(environ.get("credentials_dict"))
    return Credentials.from_service_account_info(credentials_dict).with_scopes(
        ["https://www.googleapis.com/auth/cloud-platform"]
    )

    # Configure a autenticação para a conta de serviço do GCS


def bucketGcs(storageClient: Client) -> Bucket:
    """
    Retrieve the GCS bucket object.

    Args:
        storageClient (Client): The GCS client.

    Returns:
        Bucket: The GCS bucket.
    """
    bucket_name = environ.get("bucket_name")

    bucket_obj = storageClient.bucket(bucket_name)
    return bucket_obj


def stop_execution(
    app: Flask, pid: str, robot_stop: bool = False
) -> tuple[dict[str, str], int]:
    """
    Stop the execution of a bot based on its PID.

    Args:
        app (Flask): The Flask application instance.
        pid (str): The process identifier of the bot.
        robot_stop (bool, optional): Flag to indicate robot stop. Defaults to False.

    Returns:
        tuple[dict[str, str], int]: A message and HTTP status code.
    """
    from app import db
    from app.models import Executions, ThreadBots
    from status import SetStatus

    try:
        processID = ThreadBots.query.filter(ThreadBots.pid == pid).first()

        if processID:
            get_info = (
                db.session.query(Executions).filter(Executions.pid == pid).first()
            )

            system = get_info.bot.system
            typebot = get_info.bot.type
            user = get_info.user.login
            get_info.status = "Finalizado"
            get_info.data_finalizacao = datetime.now(pytz.timezone("America/Manaus"))
            filename = get_file(pid, app)

            if filename != "":
                get_info.file_output = filename
                db.session.commit()
                db.session.close()

            elif filename == "":
                get_info.file_output = SetStatus(
                    usr=user, pid=pid, system=system, typebot=typebot
                ).botstop(db, app)
                db.session.commit()
                db.session.close()

        elif not processID:
            raise Exception("Execution not found!")

        return {"message": "bot stopped!"}, 200

    except Exception as e:
        app.logger.error("An error occurred: %s", str(e))
        return {"message": "An internal error has occurred!"}, 500


def get_file(pid: str, app: Flask) -> str:
    """
    Retrieve the output file associated with a bot's PID.

    Args:
        pid (str): The process identifier of the bot.
        app (Flask): The Flask application instance.

    Returns:
        str: The filename if found, else an empty string.
    """
    storage_client = storageClient()

    # Obtém o bucket
    bucket = bucketGcs(storage_client)

    arquivo = ""
    list_blobs: list[Blob] = list(bucket.list_blobs())
    for blob in list_blobs:
        blobnames = (
            str(blob.name).split("/")[1] if "/" in str(blob.name) else str(blob.name)
        )
        arquivo = blobnames if pid in blobnames else ""
        if pid in blobnames:
            arquivo = blobnames

            if app.testing:
                blob.delete()
            break

    return arquivo
