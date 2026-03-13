import os
from minio import Minio
from minio.error import S3Error
import io


MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

# Validation of required credentials
if not MINIO_ACCESS_KEY:
    raise ValueError("MINIO_ACCESS_KEY environment variable must be set")
if not MINIO_SECRET_KEY:
    raise ValueError("MINIO_SECRET_KEY environment variable must be set")

# Инициализация клиента Minio
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE,
)


def get_bucket_name(username: str) -> str:
    """Получение имени бакета для пользователя"""
    # S3/MinIO bucket names must be DNS-compliant (lowercase, numbers, hyphens only)
    # Replace underscores with hyphens to comply with naming rules
    safe_username = username.replace("_", "-").lower()
    return f"user-{safe_username}"


def create_bucket_if_not_exists(bucket_name: str) -> bool:
    """Создание бакета, если он не существует"""
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name, location="us-east-1")
            return True
        return False
    except S3Error as e:
        raise Exception(f"Ошибка при создании бакета: {e}")


def upload_file(bucket_name: str, file_name: str, file_data: bytes) -> bool:
    """Загрузка файла в Minio"""
    try:
        minio_client.put_object(
            bucket_name,
            file_name,
            io.BytesIO(file_data),
            len(file_data),
        )
        return True
    except S3Error as e:
        raise Exception(f"Ошибка при загрузке файла: {e}")


def list_files(bucket_name: str) -> list[str]:
    """Получение списка файлов в бакете"""
    try:
        objects = minio_client.list_objects(bucket_name)
        return [obj.object_name for obj in objects]
    except S3Error as e:
        raise Exception(f"Ошибка при получении списка файлов: {e}")


def delete_file(bucket_name: str, file_name: str) -> bool:
    """Удаление файла из бакета"""
    try:
        minio_client.remove_object(bucket_name, file_name)
        return True
    except S3Error as e:
        raise Exception(f"Ошибка при удалении файла: {e}")


def download_file(bucket_name: str, file_name: str) -> bytes:
    """Скачивание файла из бакета"""
    try:
        response = minio_client.get_object(bucket_name, file_name)
        return response.read()
    except S3Error as e:
        raise Exception(f"Ошибка при скачивании файла: {e}")
