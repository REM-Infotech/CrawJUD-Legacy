"""Module providing miscellaneous utilities including encryption, PID generation, and GCS handling."""

import json
import random
import string
from os import environ
from typing import Any

from dotenv_vault import load_dotenv
from flask import current_app as app
from google.cloud.storage import Bucket, Client
from google.oauth2.service_account import Credentials
from itsdangerous import URLSafeTimedSerializer

from .MakeTemplate import MakeModels

load_dotenv()
signed_url_lifetime = 300

__all__ = [MakeModels]


# Função para criptografar os dados do cookie
def encrypt_cookie(data: Any) -> str:
    """Encrypt data for use in cookies.

    Args:
        data: The data to encrypt.

    Returns:
        str: The encrypted data as a string.

    """
    serializer = URLSafeTimedSerializer(app.secret_key)
    return serializer.dumps(data)


# Função para descriptografar os dados do cookie
def decrypt_cookie(encrypted_data: str) -> Any | None:
    """Decrypt cookie data.

    Args:
        encrypted_data: The encrypted cookie string.

    Returns:
        The original data if decryption is successful; otherwise, None.

    """
    serializer = URLSafeTimedSerializer(app.secret_key)
    try:
        return serializer.loads(encrypted_data)
    except Exception:
        return None  # Em caso de falha na descriptografia ou expiração


def generate_pid() -> str:
    """Generate a unique PID string.

    Returns:
        str: A unique PID comprised of an interleaved string of letters and digits.

    """
    while True:
        # Gerar 4 letras maiúsculas e 4 dígitos
        letters = random.sample(string.ascii_uppercase, 6)
        digits = random.sample(string.digits, 6)

        # Intercalar letras e dígitos
        pid = "".join([letters[i // 2] if i % 2 == 0 else digits[i // 2] for i in range(6)])

        # Verificar se a string gerada não contém sequências do tipo "AABB"
        if not any(pid[i] == pid[i + 1] for i in range(len(pid) - 1)):
            return pid


def storage_client() -> Client:
    """Create a storage Client for Google Cloud Storage.

    Returns:
        Client: An authenticated GCS client.

    """
    project_id = environ.get("PROJECT_ID")
    # Configure a autenticação para a conta de serviço do GCS
    credentials = credentials_gcs()

    return Client(credentials=credentials, project=project_id)


def credentials_gcs() -> Credentials:
    """Obtain GCS credentials from environment variables.

    Returns:
        Credentials: The credentials object for GCS.

    """
    credentials_dict = json.loads(environ.get("CREDENTIALS_DICT"))
    return Credentials.from_service_account_info(credentials_dict).with_scopes([
        "https://www.googleapis.com/auth/cloud-platform"
    ])

    # Configure a autenticação para a conta de serviço do GCS


def bucket_gcs(storage_client: Client, bucket_name: str = None) -> Bucket:
    """Retrieve a bucket object from GCS.

    Args:
        storage_client (Client): The GCS client.
        bucket_name (str, optional): The name of the bucket. Defaults to None.

    Returns:
        Bucket: The bucket object.

    """
    if not bucket_name:
        bucket_name = environ.get("BUCKET_NAME")

    bucket_obj = storage_client.bucket(bucket_name)
    return bucket_obj


def generate_signed_url(blob_name: str) -> str:
    """Generate a signed URL for a given blob in GCS.

    Args:
        blob_name (str): The name of the blob.

    Returns:
        str: A signed URL with a limited lifetime.

    """
    blob = bucket_gcs(storage_client()).blob(blob_name)
    url = blob.generate_signed_url(
        expiration=signed_url_lifetime,
        method="GET",
        version="v4",
        credentials=credentials_gcs(),
    )
    return url
