from fastapi import FastAPI
from app.api.api import router

app = FastAPI(root_path="/api/rag")

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "RAG Microservice"}

