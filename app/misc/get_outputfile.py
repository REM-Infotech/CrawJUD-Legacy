from ..misc import bucketGcs, storageClient  # pragma: no cover


def get_file(pid: str) -> str:  # pragma: no cover

    storage_client = storageClient()

    # Obtém o bucket
    bucket = bucketGcs(storage_client)

    arquivo = ""

    for blob in bucket.list_blobs():

        blobnames = str(blob.name)
        if "/" in blobnames:
            blobnames = blobnames.split("/")[1]

        if pid in blobnames:
            arquivo = blobnames

    return arquivo
