import asyncio
from pathlib import Path
from typing import List, Optional, Tuple

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from .files import Files


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
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    ):
        """
        :param user_id: идентификатор пользователя
        :param directory: корневая директория для хранения данных
        :param chunk_size: размер чанка при разбиении текста
        :param chunk_overlap: перекрытие чанков
        :param embedding_model: название модели эмбеддингов из HuggingFace
        """
        self.user_id = user_id
        self.files = Files(self.user_id)
        self.main_directory = directory
        self.chromadb_directory = directory / self.user_id
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={"device": "cpu"},  # или 'cuda' при наличии GPU
            encode_kwargs={"normalize_embeddings": True},
        )

    async def load_file(self, file_path: Path) -> List[Document]:
        """Загружает один PDF-файл в фоновом потоке."""
        loader = PyMuPDFLoader(str(file_path))
        return await asyncio.to_thread(loader.load)

    async def load_files(self) -> List[Document]:
        """Загружает все файлы пользователя параллельно."""
        all_files = await self.files.download_all_files()
        tasks = [self.load_file(f) for f in all_files]
        results = await asyncio.gather(*tasks)
        # Объединяем списки документов из всех файлов
        return [doc for sublist in results for doc in sublist]

    async def text_split(self, documents: List[Document]) -> List[Document]:
        """Разбивает документы на чанки."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )
        return text_splitter.split_documents(documents)

    async def generate_vectors(self, chunks: List[Document]) -> None:
        """Создаёт векторное хранилище из чанков и сохраняет на диск."""
        print("Создание векторной базы данных...")
        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=str(self.chromadb_directory),
            collection_metadata={"hnsw:space": "cosine"},
        )
        # persist() необязателен в новых версиях Chroma, но оставлен для совместимости
        vectordb.persist()
        print("Векторная база создана и сохранена.")

    async def generate_chromadb(self) -> None:
        """Полный процесс: загрузка файлов, разбиение, создание векторного хранилища."""
        documents = await self.load_files()
        chunks = await self.text_split(documents)
        await self.generate_vectors(chunks)

    async def _get_vectordb(self) -> Chroma:
        """Возвращает загруженное векторное хранилище (синхронно, обёрнуто в to_thread)."""
        return await asyncio.to_thread(
            Chroma,
            persist_directory=str(self.chromadb_directory),
            embedding_function=self.embeddings,
        )

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
        return docs

    async def close(self):
        """Закрывает сессию файлового менеджера."""
        await self.files.close()
