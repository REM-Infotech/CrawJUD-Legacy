from ..misc import bucketGcs, storageClient


def get_file(pid: str) -> str:

    bucket_name = "outputexec-bots"
    storage_client = storageClient()

    # Obtém o bucket
    bucket = bucketGcs(storage_client, bucket_name)

    arquivo = ""

    for blob in bucket.list_blobs():

        blobnames = str(blob.name)
        if "/" in blobnames:
            blobnames = blobnames.split("/")[1]

        if pid in blobnames:
            arquivo = blobnames

    return arquivo
