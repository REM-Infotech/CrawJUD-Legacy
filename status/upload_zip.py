import os

from app.misc import bucketGcs, storageClient


def enviar_arquivo_para_gcs(zip_file: str) -> bool:

    try:
        path_output = os.path.join(os.getcwd(), zip_file)

        if os.path.exists(path_output):
            arquivo_local = path_output
            objeto_destino = os.path.basename(path_output)
        bucket = bucketGcs(storageClient(), "outputexec-bots")

        # Cria um objeto Blob no bucket
        blob = bucket.blob(objeto_destino)

        # Faz o upload do arquivo local para o objeto Blob
        blob.upload_from_filename(arquivo_local)

        return True

    except Exception as e:
        raise e
