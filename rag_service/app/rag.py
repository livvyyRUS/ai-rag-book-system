import asyncio
import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from chromadb.config import Settings as ChromaSettings
from .files import Files


embedding_model: str = os.environ.get("HF_EMBEDDINGS_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
embeddings = HuggingFaceEmbeddings(
    model_name=embedding_model,
    model_kwargs={"device": "cpu"},  # или 'cuda' при наличии GPU
    encode_kwargs={"normalize_embeddings": True},
)


class RAG:
    """
    Класс для построения RAG-системы: загрузка файлов, разделение на чанки,
    создание векторного хранилища и поиск по нему.
    """

    def __init__(
        self,
        user_id: str,
        directory: Path = Path("rag_data"),
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        :param user_id: идентификатор пользователя
        :param directory: корневая директория для хранения данных
        :param chunk_size: размер чанка при разбиении текста
        :param chunk_overlap: перекрытие чанков
        """
        self.user_id = user_id
        self.files = Files(self.user_id)
        self.main_directory = directory
        self.chromadb_directory = directory / self.user_id
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def load_file(self, file_path: Path) -> List[Document]:
        """Загружает один файл (.txt или .pdf) в фоновом потоке."""
        file_ext = file_path.suffix.lower()
        
        if file_ext == ".txt":
            loader = TextLoader(str(file_path), encoding="utf-8")
        elif file_ext == ".pdf":
            loader = PyMuPDFLoader(str(file_path))
        else:
            # По умолчанию пытаемся загрузить как текст
            loader = TextLoader(str(file_path), encoding="utf-8")
        
        documents = await asyncio.to_thread(loader.load)
        
        # Добавляем имя файла в метаданные каждого документа
        for doc in documents:
            doc.metadata["source_file"] = file_path.name
            doc.metadata["title"] = file_path.stem  # имя файла без расширения
        
        return documents

    async def load_files(self) -> List[Document]:
        """Загружает все файлы пользователя параллельно."""
        all_files = await self.files.download_all_files()
        # Convert strings to Path objects
        tasks = [self.load_file(Path(f)) for f in all_files]
        results = await asyncio.gather(*tasks)
        # Объединяем списки документов из всех файлов
        return [doc for sublist in results for doc in sublist]

    async def text_split(self, documents: List[Document]) -> List[Document]:
        """Разбивает документы на чанки в фоновом потоке."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )
        # split_documents может быть вычислительно затратным → выносим в поток
        return await asyncio.to_thread(text_splitter.split_documents, documents)

    async def generate_vectors(self, chunks: List[Document]) -> None:
        """Создаёт векторное хранилище из чанков и сохраняет на диск (в потоке)."""
        print("Создание векторной базы данных...")

        def _create_db():
            # Создаем директорию для persistence, если не существует
            self.chromadb_directory.mkdir(parents=True, exist_ok=True)
            
            # Создаем векторную базу с автосохранением
            vectordb = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=str(self.chromadb_directory),
                client_settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                )
            )
            return vectordb

        await asyncio.to_thread(_create_db)
        print("Векторная база создана и сохранена.")

    async def generate_chromadb(self) -> None:
        """Полный процесс: загрузка файлов, разбиение, создание векторного хранилища."""
        # Очищаем кэш перед загрузкой новых файлов
        await self.files.clear_cache()
        # Очищаем ChromaDB директорию для пересоздания с новыми данными
        if self.chromadb_directory.exists():
            shutil.rmtree(self.chromadb_directory)
        
        documents = await self.load_files()
        chunks = await self.text_split(documents)
        await self.generate_vectors(chunks)

    async def _get_vectordb(self) -> Chroma:
        """Возвращает загруженное векторное хранилище."""
        def _load_vectordb():
            return Chroma(
                embedding_function=embeddings,
                persist_directory=str(self.chromadb_directory),
                client_settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                )
            )
        return await asyncio.to_thread(_load_vectordb)

    async def similarity_search(
        self,
        query: str,
        k: int = 3,
        filter: Optional[dict] = None,
    ) -> List[Document]:
        """
        Базовый семантический поиск.

        :param query: текст запроса
        :param k: количество возвращаемых чанков
        :param filter: фильтр по метаданным (например, {"source": "file.pdf"})
        :return: список документов
        """
        if not self.chromadb_directory.exists():
            raise FileNotFoundError(
                f"База данных не найдена в {self.chromadb_directory}. "
                "Сначала выполните generate_chromadb()."
            )
        vectordb = await self._get_vectordb()
        docs = await asyncio.to_thread(
            vectordb.similarity_search, query, k=k, filter=filter
        )
        print(docs)
        return docs

    async def similarity_search_with_scores(
        self,
        query: str,
        k: int = 3,
        filter: Optional[dict] = None,
    ) -> List[Tuple[Document, float]]:
        """
        Семантический поиск с оценками релевантности.

        :return: список кортежей (документ, оценка)
        """
        if not self.chromadb_directory.exists():
            raise FileNotFoundError(
                f"База данных не найдена в {self.chromadb_directory}. "
                "Сначала выполните generate_chromadb()."
            )
        vectordb = await self._get_vectordb()
        docs_with_scores = await asyncio.to_thread(
            vectordb.similarity_search_with_score, query, k=k, filter=filter
        )
        print(docs_with_scores)
        return docs_with_scores

    async def similarity_search_with_mmr(
        self,
        query: str,
        k: int = 3,
        lambda_mult: float = 0.5,
        filter: Optional[dict] = None,
    ) -> List[Document]:
        """
        Поиск с использованием Maximal Marginal Relevance (MMR).
        Обеспечивает разнообразие результатов.

        :param query: текст запроса
        :param k: количество возвращаемых чанков
        :param lambda_mult: баланс между релевантностью (1.0) и разнообразием (0.0)
        :param filter: фильтр по метаданным
        :return: список документов
        """
        if not self.chromadb_directory.exists():
            raise FileNotFoundError(
                f"База данных не найдена в {self.chromadb_directory}. "
                "Сначала выполните generate_chromadb()."
            )
        vectordb = await self._get_vectordb()
        docs = await asyncio.to_thread(
            vectordb.max_marginal_relevance_search,
            query,
            k=k,
            lambda_mult=lambda_mult,
            filter=filter,
        )
        print(docs)
        return docs

    async def close(self):
        """Закрывает сессию файлового менеджера."""
        await self.files.close()
