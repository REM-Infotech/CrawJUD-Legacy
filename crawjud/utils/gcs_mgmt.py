"""Module to manage Google Cloud Storage (GCS) operations."""

import json
from pathlib import Path

from dotenv import dotenv_values
from google.cloud.storage import Bucket, Client
from google.cloud.storage.blob import Blob
from google.oauth2.service_account import Credentials

environ = dotenv_values()


def storage_client() -> Client:
    """Create a Google Cloud Storage client.

    Returns:
        Client: Configured GCS client.

    """
    project_id = environ.get("project_id")
    # Configure a autenticação para a conta de serviço do GCS
    credentials = credentials_gcs()

    return Client(credentials=credentials, project=project_id)


def credentials_gcs() -> Credentials:
    """Create Google Cloud Storage credentials from environment variables.

    Returns:
        Credentials: GCS service account credentials.

    """
    path_cred = Path(__file__).cwd().joinpath("crawjud", "bot", "temp", "cred_json.json")
    with path_cred.open("w") as f:
        f.write(environ.get("CREDENTIALS_DICT"))

    with path_cred.open("r") as f:
        credential = json.loads(f.read())

        return Credentials.from_service_account_info(credential).with_scopes(
            ["https://www.googleapis.com/auth/cloud-platform"],
        )

    # Configure a autenticação para a conta de serviço do GCS


def bucket_gcs(storage_client: Client) -> Bucket:
    """Retrieve the GCS bucket object.

    Args:
        storage_client (Client): The GCS client.

    Returns:
        Bucket: The GCS bucket.

    """
    bucket_obj = storage_client.bucket(environ.get("BUCKET_NAME"))
    return bucket_obj


def get_file(pid: str) -> str:
    """Retrieve the output file associated with a bot's PID.

    Args:
        pid (str): The process identifier of the bot.

    Returns:
        str: The filename if found, else an empty string.

    """
    # Obtém o bucket
    bucket = bucket_gcs(storage_client())

    arquivo = ""
    list_blobs: list[Blob] = list(bucket.list_blobs())
    for blob in list_blobs:
        blobnames = str(blob.name).split("/")[1] if "/" in str(blob.name) else str(blob.name)
        arquivo = blobnames if pid in blobnames else ""
        if pid in blobnames:
            arquivo = blobnames
            break

    return arquivo
