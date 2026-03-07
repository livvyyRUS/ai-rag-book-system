from fastapi import APIRouter, HTTPException, Query
from .models import (
    SimilaritySearchAnswerModel,
    SimilaritySearchAnswersModel,
    SimilaritySearchWithScoreAnswerModel,
    SimilaritySearchWithScoreAnswersModel
)
from app.rag import RAG
from app.ai.agents.rag_agent import RAGAgent
from app.ai.agents.talk_agent import TalkAgent

router = APIRouter()


@router.post("/generate_chroma_db")
async def generate_chroma_db(user_id: str = None):
    if user_id is None:
        raise HTTPException(400, "user_id is not found")
    rag = RAG(user_id=user_id)
    await rag.generate_chromadb()
    await rag.close()
    return {"status": "ok"}


@router.get("/similarity_search")
async def similarity_search(
    user_id: str = None,
    query: str = None,
    k: int = Query(3, ge=1, le=20)
):
    if user_id is None:
        raise HTTPException(400, "user_id is not found")
    if query is None:
        raise HTTPException(400, "query is not found")
    
    rag = RAG(user_id=user_id)
    try:
        documents = await rag.similarity_search(query=query, k=k)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    finally:
        await rag.close()
    
    answers = [
        SimilaritySearchAnswerModel(
            text=doc.page_content,
            title=doc.metadata.get("title"),
            page=int(doc.metadata.get("page", "0")) + 1,
        )
        for doc in documents
    ]
    return SimilaritySearchAnswersModel(answers=answers)


@router.get("/similarity_search_with_scores")
async def similarity_search_with_scores(
    user_id: str = None,
    query: str = None,
    k: int = Query(3, ge=1, le=20)
):
    if user_id is None:
        raise HTTPException(400, "user_id is not found")
    if query is None:
        raise HTTPException(400, "query is not found")
    
    rag = RAG(user_id=user_id)
    try:
        docs_with_scores = await rag.similarity_search_with_scores(query=query, k=k)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    finally:
        await rag.close()
    
    answers = [
        SimilaritySearchWithScoreAnswerModel(
            text=doc.page_content,
            title=doc.metadata.get("title"),
            page=int(doc.metadata.get("page", "0")) + 1,
            score=score
        )
        for doc, score in docs_with_scores
    ]
    return SimilaritySearchWithScoreAnswersModel(answers=answers)


@router.get("/similarity_search_mmr")
async def similarity_search_mmr(
    user_id: str = None,
    query: str = None,
    k: int = Query(3, ge=1, le=20),
    lambda_mult: float = Query(0.5, ge=0.0, le=1.0)
):
    if user_id is None:
        raise HTTPException(400, "user_id is not found")
    if query is None:
        raise HTTPException(400, "query is not found")
    
    rag = RAG(user_id=user_id)
    try:
        documents = await rag.similarity_search_with_mmr(query=query, k=k, lambda_mult=lambda_mult)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    finally:
        await rag.close()
    
    answers = [
        SimilaritySearchAnswerModel(
            text=doc.page_content,
            title=doc.metadata.get("title"),
            page=int(doc.metadata.get("page", "0")) + 1,
        )
        for doc in documents
    ]
    return SimilaritySearchAnswersModel(answers=answers)


@router.get("/chat")
async def chat(
    user_id: str, 
    query: str,
    jwt_token: 
):
    if user_id is None:
        raise HTTPException(400, "user_id is not found")
    if query is None:
        raise HTTPException(400, "query is not found")
    rag_agent = RAGAgent(user_id=user_id)
    talk_agent = TalkAgent(user_id=user_id)
    rag_answer = await rag_agent.message(query=query)
    answer = await talk_agent.message(rag_answer)
    return {
        "status": "ok",
        "text": answer
    }
    