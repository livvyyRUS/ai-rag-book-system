from langchain.tools import tool
from app.rag import RAG

def create_rag_tool(user_id: str):
    @tool
    async def rag_search(query: str) -> str:
        """Ищет информацию в документах пользователя. 
        Передавай вопрос пользователя дословно. 
        Возвращает топ релевантные фрагменты из документов с метаданными (title, page).
        Используй ТОЛЬКО когда вопрос касается содержимого документов."""
        
        rag = RAG(user_id=user_id)
        if not rag.chromadb_directory.exists():
            await rag.generate_chromadb()
            
        documents = await rag.similarity_search_with_mmr(query=query)
        
        # Форматируем как читаемый текст (агент легко анализирует)
        results = []
        for i, doc in enumerate(documents, 1):
            title = doc.metadata.get("title", "Без названия")
            page = int(doc.metadata.get("page", "0")) + 1
            content = doc.page_content[:1000] + "..." if len(doc.page_content) > 1000 else doc.page_content
            
            results.append(f"[#{i}] {title} (стр. {page})\n{content}\n{'-'*80}")
        
        formatted_results = "\n\n".join(results)
        print(f"RAG results for '{query}':\n{formatted_results[:500]}...")  # Лог
        
        return formatted_results if results else "Релевантных документов не найдено."

    return rag_search