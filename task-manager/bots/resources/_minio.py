from celery import Celery
from dotenv import load_dotenv
from minio import Minio as MinioClient

from config import config

load_dotenv()


class Minio(MinioClient):
    celery_app: Celery

    def __init__(
        self,
    ) -> None:
        dict_config = dict(list(config.as_dict().items()))
        super().__init__(
            endpoint=dict_config["MINIO_ENDPOINT"],
            access_key=dict_config.get("MINIO_ACCESS_KEY"),
            secret_key=dict_config.get("MINIO_SECRET_KEY"),
            session_token=dict_config.get("MINIO_SESSION_TOKEN"),
            secure=dict_config.get("MINIO_SECURE", False),
            region=dict_config.get("MINIO_REGION"),
            http_client=dict_config.get("MINIO_HTTP_CLIENT"),
            credentials=dict_config.get("MINIO_CREDENTIALS"),
            cert_check=dict_config.get("MINIO_CERT_CHECK", False),
        )
