import asyncio

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from .files import Files

from pathlib import Path


class RAG:
    def __init__(self, user_id: str, directory: Path = Path("rag_data")):
        self.user_id = user_id
        self.files = Files(self.user_id)
        self.main_directory = directory
        self.chromadb_directory = directory / self.user_id
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
    async def load_file(self, file_path):
        loader = PyMuPDFLoader(file_path)
        # run in thread pool because loader.load() is blocking
        return await asyncio.to_thread(loader.load)

    async def load_files(self):
        all_files = await self.files.download_all_files()
        tasks = [self.load_file(f) for f in all_files]
        results = await asyncio.gather(*tasks)
        documents = [doc for sublist in results for doc in sublist]
        return documents
    
    async def text_split(self, documents: list[Document]):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        chunks = text_splitter.split_documents(documents)
        return chunks
    
    
    async def generate_vectors(self, chunks: list[Document]):

        print("Создание векторной базы данных...")
        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=str(self.chromadb_directory)
        )

        vectordb.persist()
        
        
    async def generate_chromadb(self):
        print(
            "test"
        )
        documents = await self.load_files()
        chunks = await self.text_split(documents)
        await self.generate_vectors(chunks)
        

        
    async def similarity_search(self, query: str, k: int=3) -> list[Document]:
        print("\n--- Тестовый поиск ---")
        # Загружаем базу обратно
        loaded_vectordb = Chroma(
            persist_directory=str(self.chromadb_directory),
            embedding_function=self.embeddings
        )

        docs = loaded_vectordb.similarity_search(query, k=3)
        return docs
        # print(f"Запрос: {query}")
        # print("Наиболее релевантные фрагменты:")
        # for i, doc in enumerate(docs):
        #     print(f"\n--- Чанк {i+1} ---")
        #     print(doc.page_content)
        #     print(f"Метаданные: {doc.metadata}")
        
    async def close(self):
        await self.files.close()
                