from pydantic import BaseModel
from typing import List, Optional

class SimilaritySearchAnswerModel(BaseModel):
    text: str
    title: Optional[str]
    page: int

class SimilaritySearchAnswersModel(BaseModel):
    answers: List[SimilaritySearchAnswerModel]

class SimilaritySearchWithScoreAnswerModel(SimilaritySearchAnswerModel):
    score: float

class SimilaritySearchWithScoreAnswersModel(BaseModel):
    answers: List[SimilaritySearchWithScoreAnswerModel]
    
    
class StatusModel(BaseModel):
    status: str
    
    
class StatusWithAnswerModel(BaseModel):
    status: str
    text: str