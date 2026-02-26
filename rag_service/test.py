import httpx

# response = httpx.post("http://localhost:8000/generate_chroma_db?user_id=test", timeout=1000)
query = input()
response = httpx.get(f"http://localhost:8000/similarity_search_mmr?user_id=test&query={query}", timeout=1000)

print(response.text)
# import asyncio

# from app.rag import RAG

# rag = RAG("test")
# async def main():
#     documents = await rag.load_files()
#     print(f"Загружено документов: {len(documents)}")
#     if documents:
#         print("Первый документ:", documents[0].page_content[:200])
#         print("Метаданные:", documents[0].metadata)
#     chunks = await rag.text_split(documents)
#     print(f"Получено чанков: {len(chunks)}")
    
# asyncio.run(main())