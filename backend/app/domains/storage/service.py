from minio import Minio
from minio.error import S3Error
from app.core.config import settings

minio_client = Minio(
    settings.MINIO_ENDPOINT,      
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False,
)


def ensure_bucket(bucket_name: str):
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)


def upload_file(bucket_name: str, object_name: str, file_path: str) -> str:
    ensure_bucket(bucket_name)
    try:
        minio_client.fput_object(bucket_name, object_name, file_path)
        return f"{bucket_name}/{object_name}"
    except S3Error as e:
        raise RuntimeError(f"อัปโหลดล้มเหลว: {e}")


def get_download_url(bucket_name: str, object_name: str, expires_seconds: int = 3600) -> str:
    from datetime import timedelta
    return minio_client.presigned_get_object(
        bucket_name, object_name, expires=timedelta(seconds=expires_seconds)
    )


def list_objects(bucket_name: str) -> list[str]:
    if not minio_client.bucket_exists(bucket_name):
        return []
    return [obj.object_name for obj in minio_client.list_objects(bucket_name)]