from pydantic import BaseModel
from typing import List, Optional


class CitationModel(BaseModel):
    """Модель цитаты/источника для ответа на вопрос."""
    book: str  # название книги/файла
    location: str  # местоположение (страница, глава и т.п.)
    text: str  # текст цитаты


class SimilaritySearchAnswerModel(BaseModel):
    text: str
    title: Optional[str]
    page: int
    source_file: Optional[str] = None  # имя исходного файла


class SimilaritySearchAnswersModel(BaseModel):
    answers: List[SimilaritySearchAnswerModel]


class SimilaritySearchWithScoreAnswerModel(SimilaritySearchAnswerModel):
    score: float


class SimilaritySearchWithScoreAnswersModel(BaseModel):
    answers: List[SimilaritySearchWithScoreAnswerModel]


class StatusModel(BaseModel):
    status: str


class StatusWithAnswerModel(BaseModel):
    """Модель ответа на вопрос с цитатами."""
    status: str
    text: str
    citations: Optional[List[CitationModel]] = None  # список цитат, на которые опирался ответ