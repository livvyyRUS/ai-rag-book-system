import os
import httpx
from pydantic import BaseModel
from typing import Optional


RAG_API_URL = os.getenv("RAG_API_URL", "http://localhost:8000/api/rag")


class StatusModel(BaseModel):
    status: str


class StatusWithAnswerModel(BaseModel):
    status: str
    text: str


class SimilaritySearchAnswerModel(BaseModel):
    text: str
    title: Optional[str] = None
    page: int


class SimilaritySearchWithScoreAnswerModel(BaseModel):
    text: str
    title: Optional[str] = None
    page: int
    score: float


class SimilaritySearchAnswersModel(BaseModel):
    answers: list[SimilaritySearchAnswerModel]


class SimilaritySearchWithScoreAnswersModel(BaseModel):
    answers: list[SimilaritySearchWithScoreAnswerModel]


class RAGClient:
    """Клиент для работы с RAG API"""

    def __init__(self, jwt_token: str, user_id: str):
        self.jwt_token = jwt_token
        self.user_id = user_id
        self.base_url = RAG_API_URL

    async def generate_chroma_db(self) -> StatusModel:
        """Генерация Chroma DB для пользователя"""
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout=1000, connect=1000, read=1000, write=1000)) as client:
            response = await client.post(
                f"{self.base_url}/generate_chroma_db",
                params={"user_id": self.user_id, "jwt_token": self.jwt_token}
            )
            response.raise_for_status()
            return StatusModel(**response.json())

    async def similarity_search(self, query: str, k: int = 3) -> SimilaritySearchAnswersModel:
        """Поиск похожих документов"""
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout=1000, connect=1000, read=1000, write=1000)) as client:
            response = await client.get(
                f"{self.base_url}/similarity_search",
                params={"user_id": self.user_id, "query": query, "k": k, "jwt_token": self.jwt_token}
            )
            response.raise_for_status()
            return SimilaritySearchAnswersModel(**response.json())

    async def similarity_search_with_scores(self, query: str, k: int = 3) -> SimilaritySearchWithScoreAnswersModel:
        """Поиск похожих документов с оценками"""
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout=1000, connect=1000, read=1000, write=1000)) as client:
            response = await client.get(
                f"{self.base_url}/similarity_search_with_scores",
                params={"user_id": self.user_id, "query": query, "k": k, "jwt_token": self.jwt_token}
            )
            response.raise_for_status()
            return SimilaritySearchWithScoreAnswersModel(**response.json())

    async def similarity_search_mmr(self, query: str, k: int = 3, lambda_mult: float = 0.5) -> SimilaritySearchAnswersModel:
        """Поиск похожих документов с MMR (Maximal Marginal Relevance)"""
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout=1000, connect=1000, read=1000, write=1000)) as client:
            response = await client.get(
                f"{self.base_url}/similarity_search_mmr",
                params={"user_id": self.user_id, "query": query, "k": k, "lambda_mult": lambda_mult, "jwt_token": self.jwt_token}
            )
            response.raise_for_status()
            return SimilaritySearchAnswersModel(**response.json())

    async def chat(self, query: str) -> StatusWithAnswerModel:
        """Отправка сообщения в чат"""
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout=1000, connect=1000, read=1000, write=1000)) as client:
            response = await client.get(
                f"{self.base_url}/chat",
                params={"user_id": self.user_id, "query": query, "jwt_token": self.jwt_token}
            )
            response.raise_for_status()
            return StatusWithAnswerModel(**response.json())
