"""Upload ZIP files to Google Cloud Storage with error handling and verification."""

from pathlib import Path

from ...gcs_mgmt import bucket_gcs, storage_client


def enviar_arquivo_para_gcs(zip_file: str, file_path: Path) -> tuple[str, Path]:
    """Upload a ZIP file to Google Cloud Storage.

    Args:
        zip_file (str): The name of the ZIP file to upload.
        file_path (Path): The path to the ZIP file.

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

        bucket = bucket_gcs(storage_client())

        # Create a Blob object in the bucket
        blob = bucket.blob(objeto_destino)

        # Upload the local file to the Blob object
        blob.upload_from_filename(arquivo_local)

        return zip_file, file_path

    except Exception as e:
        raise e
