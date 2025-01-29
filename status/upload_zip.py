"""
Module for uploading ZIP files to Google Cloud Storage (GCS).
"""

import os
import pathlib
from typing import Optional

from app.misc import bucketGcs, storageClient


def enviar_arquivo_para_gcs(zip_file: str) -> Optional[str]:
    """
    Uploads a ZIP file to Google Cloud Storage.

    Args:
        zip_file (str): The name of the ZIP file to upload.

    Returns:
        Optional[str]: The basename of the uploaded file if successful, else None.

    Raises:
        Exception: If an error occurs during the upload process.
    """
    try:
        arquivo_local = ""
        objeto_destino = ""

        path_output = os.path.join(pathlib.Path(__file__).parent.resolve(), zip_file)

        if os.path.exists(path_output):
            arquivo_local = path_output
            objeto_destino = os.path.basename(path_output)
        else:
            return None

        bucket = bucketGcs(storageClient())

        # Create a Blob object in the bucket
        blob = bucket.blob(objeto_destino)

        # Upload the local file to the Blob object
        blob.upload_from_filename(arquivo_local)

        return os.path.basename(zip_file)

    except Exception as e:
        raise e
