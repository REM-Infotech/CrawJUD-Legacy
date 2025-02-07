"""Module to manage Google Cloud Storage (GCS) operations."""

import json
from os import environ

from google.cloud.storage import Bucket, Client
from google.cloud.storage.blob import Blob
from google.oauth2.service_account import Credentials
from quart import Quart


def storageClient() -> Client:  # noqa: N802
    """Create a Google Cloud Storage client.

    Returns:
        Client: Configured GCS client.

    """
    project_id = environ.get("project_id")
    # Configure a autenticação para a conta de serviço do GCS
    credentials = CredentialsGCS()

    return Client(credentials=credentials, project=project_id)


def CredentialsGCS() -> Credentials:  # noqa: N802
    """Create Google Cloud Storage credentials from environment variables.

    Returns:
        Credentials: GCS service account credentials.

    """
    credentials_dict = json.loads(environ.get("credentials_dict"))
    return Credentials.from_service_account_info(credentials_dict).with_scopes(
        ["https://www.googleapis.com/auth/cloud-platform"],
    )

    # Configure a autenticação para a conta de serviço do GCS


def bucketGcs(storageClient: Client) -> Bucket:  # noqa: N802, N803
    """Retrieve the GCS bucket object.

    Args:
        storageClient (Client): The GCS client.

    Returns:
        Bucket: The GCS bucket.

    """
    bucket_name = environ.get("bucket_name")

    bucket_obj = storageClient.bucket(bucket_name)
    return bucket_obj


def get_file(pid: str, app: Quart) -> str:
    """Retrieve the output file associated with a bot's PID.

    Args:
        pid (str): The process identifier of the bot.
        app (Quart): The Quart application instance.

    Returns:
        str: The filename if found, else an empty string.

    """
    storage_client = storageClient()

    # Obtém o bucket
    bucket = bucketGcs(storage_client)

    arquivo = ""
    list_blobs: list[Blob] = list(bucket.list_blobs())
    for blob in list_blobs:
        blobnames = str(blob.name).split("/")[1] if "/" in str(blob.name) else str(blob.name)
        arquivo = blobnames if pid in blobnames else ""
        if pid in blobnames:
            arquivo = blobnames

            if app.testing:
                blob.delete()
            break

    return arquivo
