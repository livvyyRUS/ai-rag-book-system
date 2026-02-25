from fastapi import APIRouter, HTTPException
from .models import SimilaritySearchAnswerModel, SimilaritySearchAnswersModel
from app.rag import RAG

router = APIRouter()


@router.post("/generate_chroma_db")
async def generate_chroma_db(user_id: str = None):
    if user_id is None:
        return HTTPException(400, "user_id is not found")
    rag = RAG(user_id=user_id)
    await rag.generate_chromadb()
    await rag.close()
    return {"status": "ok"}


@router.get("/similarity_search")
async def similarity_search(user_id: str = None, query: str = None, k: int = 3):
    if user_id is None:
        return HTTPException(400, "user_id is not found")
    if query is None:
        return HTTPException(400, "query is not found")
    rag = RAG(user_id=user_id)
    documents = await rag.similarity_search(query=query, k=k)
    answers = [
        SimilaritySearchAnswerModel(
            text=doc.page_content,
            title=doc.metadata.get("title"),
            page=int(doc.metadata.get("page", "0")) + 1,
        )
        for doc in documents
    ]
    await rag.close()
    return SimilaritySearchAnswersModel(answers=answers)
