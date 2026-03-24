import os
import asyncio
import uuid
import shutil
import aiofiles
from pathlib import Path
from typing import List, Optional
from miniopy_async.api import Minio


class Files:
    """
    Класс для работы с Minio: выгрузка (скачивание) и загрузка (отправка) файлов.
    Поддерживает отдельные операции для базы данных ChromaDB и для всех остальных файлов.
    """

    def __init__(self, bucket_name: str, download_dir: str = "cache"):
        """
        :param bucket_name: имя бакета в Minio
        :param download_dir: локальная директория для скачанных файлов (по умолчанию 'downloads')
        """
        self._bucket_name = bucket_name
        self._download_dir = Path(download_dir) / bucket_name
        self.client = Minio(
            os.environ.get("MINIO_HOST", "localhost:9000"),
            access_key=os.environ.get("MINIO_USER", "admin"),
            secret_key=os.environ.get("MINIO_PASSWORD", "password"),
            secure=False,
            cert_check=False,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def close(self):
        """Закрытие сессии клиента Minio."""
        await self.client.close_session()

    async def init_user_bucket(self):
        """Создание бакета, если он не существует."""
        bucket_exists = await self.client.bucket_exists(self._bucket_name)
        if not bucket_exists:
            await self.client.make_bucket(self._bucket_name)

    def _ensure_download_dir(self):
        """Создание локальной папки для скачивания, если её нет."""
        Path(self._download_dir).mkdir(parents=True, exist_ok=True)

    async def clear_cache(self):
        """Очистка локального кэша файлов."""
        if self._download_dir.exists():
            shutil.rmtree(self._download_dir)
        self._download_dir.mkdir(parents=True, exist_ok=True)

    async def list_objects(self) -> List[str]:
        """
        Получение списка всех объектов в бакете.

        :return: список имён объектов
        """
        objects = await self.client.list_objects(self._bucket_name, recursive=True)
        return [obj.object_name for obj in objects]

    # ==================== ВЫГРУЗКА (СКАЧИВАНИЕ) ====================

    async def download_file(self, object_name: str, local_path: Optional[str] = None) -> str:
        """
        Скачивание одного файла из Minio.

        :param object_name: имя объекта в Minio
        :param local_path: желаемый локальный путь (если не указан, генерируется в папке download_dir)
        :return: локальный путь к скачанному файлу
        """
        self._ensure_download_dir()

        # Если локальный путь не указан, генерируем уникальное имя в папке загрузок
        if local_path is None:
            suffix = Path(object_name).suffix
            local_path = str(Path(self._download_dir) / f"{uuid.uuid4().hex}{suffix}")

        # Создаём родительские директории, если нужно
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)

        # Скачиваем объект
        obj_data = await self.client.get_object(self._bucket_name, object_name)

        async with aiofiles.open(local_path, "wb") as f:
            async for chunk in obj_data.content:
                await f.write(chunk)

        return local_path

    async def download_files(self, object_names: List[str]) -> List[str]:
        """
        Скачивание нескольких файлов из Minio.

        :param object_names: список имён объектов
        :return: список локальных путей к скачанным файлам
        """
        return [await self.download_file(obj) for obj in object_names]

    async def download_all_files(self) -> List[str]:
        """
        Скачивание всех файлов из бакета.

        :return: список локальных путей к скачанным файлам
        """
        all_objects = await self.list_objects()
        to_download = [obj for obj in all_objects]
        return await self.download_files(to_download)

    # ==================== ЗАГРУЗКА (ОТПРАВКА) ====================

    async def upload_file(self, local_file_path: str, object_name: Optional[str] = None) -> str:
        """
        Загрузка одного файла в Minio.

        :param local_file_path: путь к локальному файлу
        :param object_name: желаемое имя объекта в Minio (если не указано, берётся имя файла)
        :return: имя объекта в Minio
        """
        if not os.path.isfile(local_file_path):
            raise FileNotFoundError(f"Локальный файл не найден: {local_file_path}")

        if object_name is None:
            object_name = Path(local_file_path).name

        await self.client.fput_object(self._bucket_name, object_name, local_file_path)
        return object_name

    async def upload_files(self, local_file_paths: List[str], object_names: Optional[List[str]] = None) -> List[str]:
        """
        Загрузка нескольких файлов в Minio.

        :param local_file_paths: список локальных путей
        :param object_names: список желаемых имён объектов (должен совпадать по длине с local_file_paths, если указан)
        :return: список имён загруженных объектов
        """
        if object_names is None:
            object_names = [None] * len(local_file_paths)
        elif len(object_names) != len(local_file_paths):
            raise ValueError("Длина списка object_names должна совпадать с длиной local_file_paths")

        results = []
        for local_path, obj_name in zip(local_file_paths, object_names):
            uploaded = await self.upload_file(local_path, obj_name)
            results.append(uploaded)
        return results


# Пример использования
if __name__ == "__main__":
    async def main():
        async with Files("test") as files:
            # Инициализация бакета (если нужно)
            await files.init_user_bucket()

            # Загрузка отдельных файлов
            await files.upload_file("example.txt")
            await files.upload_file("data.csv", "custom_name.csv")

    asyncio.run(main())