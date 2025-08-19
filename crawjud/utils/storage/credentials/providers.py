"""Gerencie provedores de credenciais para autenticação em serviços de armazenamento.

Este módulo define classes e funções para fornecer credenciais de autenticação
automatizada, incluindo integração com Google Cloud Storage e MinIO.

"""

from __future__ import annotations

import json
from os import environ

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials as GoogleCredentials
from minio.credentials.credentials import Credentials
from minio.credentials.providers import Provider

load_dotenv()


class GoogleStorageCredentialsProvider(Provider):
    """Forneça credenciais do Google Cloud Storage para autenticação automatizada.

    Args:
        Nenhum argumento é passado diretamente para esta classe.

    Returns:
        GoogleStorageCredentialsProvider: Instância do provedor de credenciais.

    Raises:
        KeyError: Caso a variável de ambiente 'GCS_CREDENTIALS' não esteja definida.

    """

    def retrieve(self) -> Credentials:
        json_credentials = json.loads(environ["GCS_CREDENTIALS"])
        credentials = GoogleCredentials.from_service_account_info(
            json_credentials,
        )
        credentials = GoogleCredentials.with_scopes(
            ["https://www.googleapis.com/auth/cloud-platform"],
        )

        return Credentials(
            access_key=credentials.token,
            expiration=credentials.expiry,
        )
