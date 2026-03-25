from typing import Any, Dict, Optional
from langchain.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent
from app.ai.llm import llm
from app.ai.tools.rag_tool import create_rag_tool
from app.ai.prompt_rewriter import get_prompt_rewriter
import json
import re


SYSTEM_PROMPT = """You are a document search extractor. Your ONLY job: search user documents and return results as JSON.

## CRITICAL ANTI-HALLUCINATION RULES
- NEVER fabricate book titles, page numbers, or text content
- NEVER invent information that is not in the rag_search results
- NEVER modify or "correct" information from search results (e.g., if a fragment says "Pushkin" but you know it should be "Dostoevsky" — DO NOT change it)
- If rag_search returns empty or "Релевантных документов не найдено" → return found=false, fragments=[]
- Extract ONLY what exists in the search results - word for word
- Do NOT guess, assume, or fill in missing information
- Copy book titles, locations, and text EXACTLY as they appear in search results

## OUTPUT FORMAT (MANDATORY)
Your final response MUST be a valid JSON object with this exact structure:

{
  "query": "original user query string",
  "found": true,
  "fragments": [
    {
      "book": "document title from metadata EXACTLY as written",
      "location": "Page X or empty string EXACTLY as written",
      "text": "exact fragment text from search results"
    }
  ]
}

## WORKFLOW
1. You will receive an OPTIMIZED query (already rewritten for better search)
2. Call the `rag_search` tool ONCE with the provided optimized query (max 1 call)
3. Parse the search results EXACTLY as they appear
4. Extract each fragment into the JSON structure above
5. Return ONLY the JSON object - nothing else

## PARSING SEARCH RESULTS
The rag_search tool returns fragments in this format:
```
[#1] Book Title (стр. 15)
Fragment text content here...
--------------------------------------------------------------------------------

[#2] Another Book (стр. 42)
More fragment text...
```

Extract each fragment EXACTLY:
- book: The title before "(стр. X)" - copy exactly as written, DO NOT modify
- location: "стр. X" (the number from parentheses) - copy exactly
- text: The content between the title line and the dashes - copy exactly, do not modify

## EXAMPLES

User: "Who is Raskolnikov?"
Optimized query: "Раскольников Родион характеристика описание студент главный герой"
rag_search returns: "[#1] Преступление и наказание (стр. 15)\nРодион Раскольников — бывший студент..."

Your response:
{"query": "Who is Raskolnikov?", "found": true, "fragments": [{"book": "Преступление и наказание", "location": "стр. 15", "text": "Родион Раскольников — бывший студент..."}]}

User: "Who is Pierre Bezukhov?"
Optimized query: "Пьер Безухов описание"
rag_search returns: "Релевантных документов не найдено."

Your response:
{"query": "Who is Pierre Bezukhov?", "found": false, "fragments": []}

## REMINDERS
- Output JSON ONLY - no markdown, no code blocks, no explanations
- The response must be parseable by json.loads() as a Python dict
- Do not return a list, string, or any other type - ONLY a dict/object
- Make EXACTLY 1 rag_search call, not more
- Copy all text EXACTLY from search results - DO NOT modify, correct, or improve anything
- Use the optimized query provided in the user message - DO NOT modify it further
"""


class RAGAgent:
    """RAG-агент для поиска в документах пользователя."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.tools = [create_rag_tool(user_id)]
        self.prompt_rewriter = get_prompt_rewriter()

        self.agent = create_agent(
            model=llm.bind_tools(self.tools),
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT
        )

    async def _parse_search_results(self, search_output: str) -> list:
        """Парсит результаты поиска из формата rag_search в список фрагментов."""
        fragments = []

        if not search_output or search_output == "Релевантных документов не найдено.":
            return fragments

        # Разбиваем по разделителям фрагментов
        fragment_pattern = r'\[#(\d+)\]\s*(.+?)\s*\(стр\.?\s*(\d+)\)\n(.*?)(?=\n-{20,}|\n\n\[#|\Z)'

        matches = re.findall(fragment_pattern, search_output, re.DOTALL)

        for match in matches:
            try:
                fragment_num, book_title, page_num, text_content = match
                fragments.append({
                    "book": book_title.strip(),
                    "location": f"стр. {page_num.strip()}",
                    "text": text_content.strip()
                })
            except (ValueError, IndexError) as e:
                print(f"⚠️ Ошибка парсинга фрагмента: {e}")
                continue

        # Если regex не сработал, пробуем альтернативный метод
        if not fragments:
            # Разбиваем по разделителям
            raw_fragments = re.split(r'\n-{20,}\n\n', search_output)

            for raw_frag in raw_fragments:
                raw_frag = raw_frag.strip()
                if not raw_frag:
                    continue

                lines = raw_frag.split('\n', 2)
                if len(lines) >= 2:
                    # Первая строка: [#N] Book Title (стр. X)
                    header_match = re.match(r'\[#\d+\]\s*(.+?)\s*\(стр\.?\s*(\d+)\)', lines[0])
                    if header_match:
                        book_title = header_match.group(1).strip()
                        page_num = header_match.group(2).strip()
                        text_content = lines[1].strip() if len(lines) > 1 else ""

                        fragments.append({
                            "book": book_title,
                            "location": f"стр. {page_num}",
                            "text": text_content
                        })

        return fragments

    async def message(self, query: str) -> Dict[str, Any]:
        """Обработка вопроса пользователя. Возвращает JSON с результатами поиска."""
        # Шаг 1: Переписываем промпт для улучшения поиска
        optimized_query = await self.prompt_rewriter.rewrite(query)

        # Шаг 2: Запускаем агента с оптимизированным запросом
        result: Dict[str, Any] = await self.agent.ainvoke({
            "messages": [HumanMessage(content=f"Original query: {query}\nOptimized query: {optimized_query}")]
        })

        messages = result["messages"]
        response = messages[-1].content

        # Парсим JSON из ответа
        try:
            # Очищаем ответ от markdown-обёрток
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()

            parsed = json.loads(clean_response)

            # Проверяем, что parsed — это dict, а не список или другой тип
            if not isinstance(parsed, dict):
                print(f"🤖RAG: unexpected response type: {type(parsed).__name__}")
                print(f"Получен ответ: {response[:200]}")
                # Пытаемся спарсить результаты напрямую из ответа
                fragments = await self._parse_search_results(response)
                return {
                    "query": query,
                    "found": len(fragments) > 0,
                    "fragments": fragments
                }

            # Если found не установлен, но есть фрагменты - устанавливаем true
            if 'found' not in parsed or parsed['found'] is None:
                parsed['found'] = len(parsed.get('fragments', [])) > 0

            print(f"🤖RAG: found={parsed.get('found')}, fragments={len(parsed.get('fragments', []))}")
            return parsed
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Ошибка парсинга JSON от RAG-агента: {e}")
            print(f"Получен ответ: {response[:200]}")
            # Пытаемся извлечь фрагменты напрямую из ответа
            fragments = await self._parse_search_results(response)
            if fragments:
                print(f"🤖RAG: parsed {len(fragments)} fragments from raw response")
                return {
                    "query": query,
                    "found": True,
                    "fragments": fragments
                }
            # Возвращаем пустой результат при ошибке
            return {
                "query": query,
                "found": False,
                "fragments": []
            }

    def __repr__(self) -> str:
        return f"RAGAgent(user_id='{self.user_id}', tools={len(self.tools)})"
