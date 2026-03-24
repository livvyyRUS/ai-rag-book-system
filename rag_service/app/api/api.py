from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import List
from .models import (
    SimilaritySearchAnswerModel,
    SimilaritySearchAnswersModel,
    SimilaritySearchWithScoreAnswerModel,
    SimilaritySearchWithScoreAnswersModel,
    StatusModel,
    StatusWithAnswerModel,
    CitationModel,
    ClearHistoryRequestModel,
    ClearHistoryResponseModel,
)
from app.rag import RAG
from app.ai.agents.rag_agent import RAGAgent
from app.ai.agents.talk_agent import TalkAgent
from app.files import Files
from app.ai.get_session_history import clear_session_history

from app.jwt import decode_jwt
from jwt import DecodeError, ExpiredSignatureError

router = APIRouter()


@router.post("/upload_books")
async def upload_books(
    files: List[UploadFile] = File(...),
    user_id: str = None,
    jwt_token: str = None,
) -> StatusModel:
    """Загрузка книг пользователя в систему.
    
    Поддерживаемые форматы: .txt, .pdf
    """
    if user_id is None:
        raise HTTPException(400, "user_id is not found")
    try:
        payload = decode_jwt(jwt_token=jwt_token)
        if payload.user_id != user_id:
            raise HTTPException(400, "Wrong token")
    except DecodeError as e:
        raise HTTPException(400, "Wrong token")
    except ExpiredSignatureError as e:
        raise HTTPException(400, "Token expired")
    
    # Валидация расширений файлов
    allowed_extensions = {".txt", ".pdf"}
    uploaded_files = []
    
    for file in files:
        file_ext = file.filename.split(".")[-1].lower()
        if f".{file_ext}" not in allowed_extensions:
            raise HTTPException(400, f"Неподдерживаемый формат файла: {file.filename}. Допустимы только .txt и .pdf")
        
        # Сохраняем файл временно
        import tempfile
        import shutil
        from pathlib import Path
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        uploaded_files.append(tmp_path)
    
    # Загружаем файлы в Minio
    async with Files(user_id) as files_manager:
        await files_manager.init_user_bucket()
        object_names = []
        for tmp_path in uploaded_files:
            file_name = Path(tmp_path).name
            await files_manager.upload_file(tmp_path, file_name)
            object_names.append(file_name)
            # Удаляем временный файл
            Path(tmp_path).unlink()
    
    return StatusModel(status=f"Загружено файлов: {len(object_names)}")


@router.post("/generate_chroma_db")
async def generate_chroma_db(user_id: str = None, jwt_token: str = None) -> StatusModel:
    if user_id is None:
        raise HTTPException(400, "user_id is not found")
    try:
        payload = decode_jwt(jwt_token=jwt_token)
        if payload.user_id != user_id:
            raise HTTPException(400, "Wrong token")
    except DecodeError as e:
        raise HTTPException(400, "Wrong token")
    except ExpiredSignatureError as e:
        raise HTTPException(400, "Token expired")

    rag = RAG(user_id=user_id)
    await rag.generate_chromadb()
    await rag.close()
    return StatusModel(status="ok")


@router.get("/similarity_search")
async def similarity_search(
    user_id: str = None,
    query: str = None,
    k: int = Query(3, ge=1, le=20),
    jwt_token: str = None,
) -> SimilaritySearchAnswersModel:
    if user_id is None:
        raise HTTPException(400, "user_id is not found")
    if query is None:
        raise HTTPException(400, "query is not found")
    try:
        payload = decode_jwt(jwt_token=jwt_token)
        if payload.user_id != user_id:
            raise HTTPException(400, "Wrong token")
    except DecodeError as e:
        raise HTTPException(400, "Wrong token")
    except ExpiredSignatureError as e:
        raise HTTPException(400, "Token expired")

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
            source_file=doc.metadata.get("source_file"),
        )
        for doc in documents
    ]
    return SimilaritySearchAnswersModel(answers=answers)


@router.get("/similarity_search_with_scores")
async def similarity_search_with_scores(
    user_id: str = None,
    query: str = None,
    k: int = Query(3, ge=1, le=20),
    jwt_token: str = None,
) -> SimilaritySearchWithScoreAnswersModel:
    if user_id is None:
        raise HTTPException(400, "user_id is not found")
    if query is None:
        raise HTTPException(400, "query is not found")
    try:
        payload = decode_jwt(jwt_token=jwt_token)
        if payload.user_id != user_id:
            raise HTTPException(400, "Wrong token")
    except DecodeError as e:
        raise HTTPException(400, "Wrong token")
    except ExpiredSignatureError as e:
        raise HTTPException(400, "Token expired")

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
            source_file=doc.metadata.get("source_file"),
            score=score,
        )
        for doc, score in docs_with_scores
    ]
    return SimilaritySearchWithScoreAnswersModel(answers=answers)


@router.get("/similarity_search_mmr")
async def similarity_search_mmr(
    user_id: str = None,
    query: str = None,
    k: int = Query(3, ge=1, le=20),
    lambda_mult: float = Query(0.5, ge=0.0, le=1.0),
    jwt_token: str = None,
) -> SimilaritySearchAnswersModel:
    if user_id is None:
        raise HTTPException(400, "user_id is not found")
    if query is None:
        raise HTTPException(400, "query is not found")
    try:
        payload = decode_jwt(jwt_token=jwt_token)
        if payload.user_id != user_id:
            raise HTTPException(400, "Wrong token")
    except DecodeError as e:
        raise HTTPException(400, "Wrong token")
    except ExpiredSignatureError as e:
        raise HTTPException(400, "Token expired")

    rag = RAG(user_id=user_id)
    try:
        documents = await rag.similarity_search_with_mmr(
            query=query, k=k, lambda_mult=lambda_mult
        )
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    finally:
        await rag.close()

    answers = [
        SimilaritySearchAnswerModel(
            text=doc.page_content,
            title=doc.metadata.get("title"),
            page=int(doc.metadata.get("page", "0")) + 1,
            source_file=doc.metadata.get("source_file"),
        )
        for doc in documents
    ]
    return SimilaritySearchAnswersModel(answers=answers)


@router.get("/chat")
async def chat(user_id: str, query: str, jwt_token: str) -> StatusWithAnswerModel:
    if user_id is None:
        raise HTTPException(400, "user_id is not found")
    if query is None:
        raise HTTPException(400, "query is not found")
    try:
        payload = decode_jwt(jwt_token=jwt_token)
        if payload.user_id != user_id:
            raise HTTPException(400, "Wrong token")
    except DecodeError as e:
        raise HTTPException(400, "Wrong token")
    except ExpiredSignatureError as e:
        raise HTTPException(400, "Token expired")

    rag_agent = RAGAgent(user_id=user_id)
    talk_agent = TalkAgent(user_id=user_id)

    # RAG-агент возвращает dict с query, found, fragments
    rag_result = await rag_agent.message(query=query)
    fragments = rag_result.get("fragments", [])

    # Передаём структурированные данные в Talk-агент
    answer = await talk_agent.message(
        query=query,
        found=rag_result.get("found", False),
        fragments=fragments
    )

    # Формируем список цитат из фрагментов
    citations = []
    for frag in fragments:
        citations.append(CitationModel(
            book=frag.get("book", "Неизвестно"),
            location=frag.get("location", ""),
            text=frag.get("text", "")
        ))

    return StatusWithAnswerModel(
        status="ok",
        text=answer,
        citations=citations if citations else None
    )


@router.post("/clear_history", response_model=ClearHistoryResponseModel)
async def clear_history(request: ClearHistoryRequestModel) -> ClearHistoryResponseModel:
    """Очищает историю сообщений конкретного пользователя в RAG-сервисе.
    
    Удаляет всю историю диалогов пользователя из памяти, что позволяет начать разговор заново.
    """
    try:
        payload = decode_jwt(jwt_token=request.jwt_token)
        if payload.user_id != request.user_id:
            raise HTTPException(400, "Wrong token")
    except DecodeError as e:
        raise HTTPException(400, "Wrong token")
    except ExpiredSignatureError as e:
        raise HTTPException(400, "Token expired")
    
    cleared = clear_session_history(session_id=request.user_id)
    
    return ClearHistoryResponseModel(
        status="ok",
        cleared=cleared
    )

