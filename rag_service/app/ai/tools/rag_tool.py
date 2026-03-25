from langchain.tools import tool
from app.rag import RAG

def create_rag_tool(user_id: str):
    @tool
    async def rag_search(query: str) -> str:
        """Ищет информацию в документах пользователя.
        Используй оптимизированный запрос как есть, без изменений.
        Возвращает топ релевантные фрагменты из документов с метаданными (title, page).
        Используй ТОЛЬКО когда вопрос касается содержимого документов.
        Возвращает до 10 фрагментов для полноты поиска."""

        rag = RAG(user_id=user_id)
        if not rag.chromadb_directory.exists():
            await rag.generate_chromadb()

        # Увеличиваем k до 10 для более полного поиска
        documents = await rag.similarity_search_with_mmr(query=query, k=10, lambda_mult=0.3)

        # Форматируем как читаемый текст (агент легко анализирует)
        results = []
        for i, doc in enumerate(documents, 1):
            title = doc.metadata.get("title", "Без названия")
            page = int(doc.metadata.get("page", "0")) + 1
            content = doc.page_content[:1500] + "..." if len(doc.page_content) > 1500 else doc.page_content

            results.append(f"[#{i}] {title} (стр. {page})\n{content}\n{'-'*80}")

        formatted_results = "\n\n".join(results)
        print(f"RAG results for '{query}': найдено {len(results)} фрагментов")  # Лог

        return formatted_results if results else "Релевантных документов не найдено."

    return rag_search