from pydantic import BaseModel


class SimilaritySearchAnswerModel(BaseModel):
    text: str
    title: str
    page: int

class SimilaritySearchAnswersModel(BaseModel):
    answers: list[SimilaritySearchAnswerModel]
    