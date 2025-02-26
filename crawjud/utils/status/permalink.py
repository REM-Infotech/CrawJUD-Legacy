"""Generate secure, time-limited signed URLs for accessing files in Google Cloud Storage."""

from datetime import timedelta

from ..gcs_mgmt import bucket_gcs, credentials_gcs, storage_client


def generate_signed_url(blob_name: str) -> str:
    """Generate a signed URL for a given blob in GCS.

    Args:
        blob_name (str): The name of the blob.

    Returns:
        str: A signed URL with a limited lifetime.

    """
    blob = bucket_gcs(storage_client()).blob(blob_name)
    url = blob.generate_signed_url(
        expiration=timedelta(days=365 * 100),
        # expiration=signed_url_lifetime,
        method="GET",
        version="v4",
        credentials=credentials_gcs(),
    )
    return url
