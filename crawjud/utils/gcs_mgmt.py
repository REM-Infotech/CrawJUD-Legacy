"""Module to manage Google Cloud Storage (GCS) operations."""

import json
from os import environ
from pathlib import Path

from google.cloud.storage import Bucket, Client
from google.cloud.storage.blob import Blob
from google.oauth2.service_account import Credentials


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
    return Credentials.from_service_account_info(json.loads(environ.get("CREDENTIALS_DICT"))).with_scopes(
        ["https://www.googleapis.com/auth/cloud-platform"],
    )

    # Configure a autenticação para a conta de serviço do GCS


def bucket_gcs(storage_client: Client, bucket: str = None) -> Bucket:
    """Retrieve the GCS bucket object.

    Args:
        storage_client (Client): The GCS client.
        bucket (str, optional): The name of the bucket. Defaults to None.

    Returns:
        Bucket: The GCS bucket.

    """
    bucket = bucket if bucket else environ.get("BUCKET_NAME")

    bucket_obj = storage_client.bucket(bucket)
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


def enviar_arquivo_para_gcs(zip_file: str, file_path: Path, bucket_name: str = None) -> tuple[str, Path]:
    """Upload a ZIP file to Google Cloud Storage.

    Args:
        zip_file (str): The name of the ZIP file to upload.
        file_path (Path): The path to the ZIP file.
        bucket_name (str, optional): The name of the bucket. Defaults to None.

    Returns:
        Optional[str]: The basename of the uploaded file if successful, else None.

    Raises:
        Exception: If an error occurs during the upload process.

    """
    try:
        arquivo_local = ""
        objeto_destino = ""

        path_output = Path(file_path)

        if path_output.exists():
            arquivo_local = str(file_path)
            objeto_destino = zip_file
        else:
            return None

        bucket = bucket_gcs(storage_client(), bucket=bucket_name)

        # Create a Blob object in the bucket
        blob = bucket.blob(objeto_destino)

        # Upload the local file to the Blob object
        blob.upload_from_filename(arquivo_local)

        return zip_file, file_path

    except Exception as e:
        raise e
