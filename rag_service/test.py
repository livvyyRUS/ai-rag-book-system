import asyncio
from app.rag import RAG


async def main():
    rag = RAG("test")
    # await rag.generate_chromadb()
    await rag.similarity_search("Государственное издательство «Художественная литература» Москва, 1937—1940")


asyncio.run(main())

