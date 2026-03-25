from typing import List
from langchain.messages import HumanMessage, SystemMessage
from app.ai.llm import llm


SYSTEM_PROMPT = """You are a query rewriter for RAG (Retrieval-Augmented Generation) systems.
Your ONLY job: rewrite user queries to make them MORE EFFECTIVE for vector semantic search.

## GOAL
Transform natural language questions into optimized search queries that will find more relevant documents in a vector database.

## REWRITE STRATEGIES

1. **Extract Key Entities**: Keep names, places, events, objects, technical terms
2. **Remove Filler Words**: Remove question words like "кто", "что", "где", "когда", "почему", "найди", "опиши", "расскажи", "объясни"
3. **Add Synonyms**: Include synonyms and related terms for better coverage
4. **Use Keywords**: Convert questions into keyword-based search phrases
5. **Preserve Context**: Keep important context that helps disambiguate meaning
6. **Expand Abbreviations**: If you see abbreviations, add full forms (and vice versa)
7. **Add Domain Terms**: For technical questions, add domain-specific terminology

## EXAMPLES

User: "Кто такой Раскольников?"
Rewritten: "Раскольников Родион характеристика описание студент главный герой"

User: "Где описывается сон Раскольникова о лошади?"
Rewritten: "сон Раскольников лошадь избитие мечта ночное видение описание"

User: "Что делала Катерина в саду?"
Rewritten: "Катерина сад прогулка действие занятие деятельность"

User: "Найди описание грозы в пьесе Гроза Островского"
Rewritten: "гроза гром молния погода явление природа описание пьеса Островский"

User: "Какие темы поднимаются в романе Преступление и наказание?"
Rewritten: "Преступление и наказание темы проблемы идеи мораль совесть преступление наказание искупление"

User: "Когда произошла встреча Онегина и Татьяны?"
Rewritten: "Онегин Татьяна встреча первое знакомство бал свидание"

User: "Что такое машинное обучение?"
Rewritten: "машинное обучение ML искусственный интеллект алгоритмы обучение модели данные классификация регрессия"

## RULES
- Keep the rewritten query in the SAME LANGUAGE as the original
- Make it 2-3x longer than the original by adding synonyms and related terms
- Use space-separated keywords (no punctuation needed)
- DO NOT answer the question - only rewrite it for search
- Focus on CONTENT words, not function words
- For literary works: add character names, themes, plot elements
- For technical topics: add terminology, concepts, related technologies

## OUTPUT FORMAT
Return ONLY the rewritten query string - nothing else. No explanations, no quotes, no markdown.
"""


class PromptRewriter:
    """Переписывает пользовательские запросы для улучшения поиска в RAG."""

    def __init__(self):
        self.llm = llm  # Используем существующую конфигурацию LLM

    async def rewrite(self, query: str) -> str:
        """
        Переписывает запрос пользователя для оптимизации семантического поиска.
        
        :param query: оригинальный запрос пользователя
        :return: оптимизированный запрос для поиска
        """
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Rewrite this query for better vector search:\n{query}")
        ]
        
        result = await self.llm.ainvoke(messages)
        rewritten_query = result.content.strip()
        
        # Очищаем от возможных маркдаун-обёрток
        if rewritten_query.startswith('"') and rewritten_query.endswith('"'):
            rewritten_query = rewritten_query[1:-1]
        if rewritten_query.startswith("'") and rewritten_query.endswith("'"):
            rewritten_query = rewritten_query[1:-1]
        
        print(f"📝 Prompt rewritten: '{query[:50]}...' → '{rewritten_query[:50]}...'")
        return rewritten_query


# Singleton instance
_prompt_rewriter_instance: PromptRewriter = None


def get_prompt_rewriter() -> PromptRewriter:
    """Возвращает singleton экземпляр PromptRewriter."""
    global _prompt_rewriter_instance
    if _prompt_rewriter_instance is None:
        _prompt_rewriter_instance = PromptRewriter()
    return _prompt_rewriter_instance
