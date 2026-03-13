from typing import Any, Dict, Optional
from langchain.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent
from app.ai.llm import llm
from app.ai.tools.rag_tool import create_rag_tool
import json


SYSTEM_PROMPT = """You are a document search extractor. Your ONLY job: search user documents and return results as JSON.

## OUTPUT FORMAT (MANDATORY)
Your final response MUST be a valid JSON object with this exact structure:

{
  "query": "original user query string",
  "found": true,
  "fragments": [
    {
      "book": "document title from metadata",
      "location": "Page X or empty string",
      "text": "exact fragment text from search results"
    }
  ]
}

## WORKFLOW
1. Call the `rag_search` tool with the user's query
2. Parse the search results (format: "[#N] Title (Page X)\\ncontent\\n---")
3. Extract each fragment into the JSON structure above
4. Return ONLY the JSON object - nothing else

## CRITICAL RULES
- NEVER answer the user's question - only extract fragments
- NEVER fabricate data - use ONLY what rag_search returns
- NEVER add commentary, explanations, or text outside the JSON
- If rag_search returns "Релевантных документов не найдено" → set found=false, fragments=[]
- Include ALL relevant fragments from search results - even partially relevant ones
- Maximum 2 tool calls per query

## PARSING SEARCH RESULTS
The rag_search tool returns fragments in this format:
```
[#1] Book Title (Page 15)
Fragment text content here...
--------------------------------------------------------------------------------

[#2] Another Book (Page 42)
More fragment text...
```

Extract each fragment:
- book: The title before "(Page X)"
- location: "Page X" (the number from parentheses)
- text: The content between the title line and the dashes

## EXAMPLES

User: "Who is Raskolnikov?"
rag_search returns: "[#1] Crime and Punishment (Page 15)\\nRodya Raskolnikov is a former student..."

Your response:
{"query": "Who is Raskolnikov?", "found": true, "fragments": [{"book": "Crime and Punishment", "location": "Page 15", "text": "Rodya Raskolnikov is a former student..."}]}

User: "Who is Pierre Bezukhov?"
rag_search returns: "Релевантных документов не найдено."

Your response:
{"query": "Who is Pierre Bezukhov?", "found": false, "fragments": []}

## REMINDERS
- Output JSON ONLY - no markdown, no code blocks, no explanations
- The response must be parseable by json.loads() as a Python dict
- Do not return a list, string, or any other type - ONLY a dict/object
"""


class RAGAgent:
    """RAG-агент для поиска в документах пользователя."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.tools = [create_rag_tool(user_id)]

        self.agent = create_agent(
            model=llm.bind_tools(self.tools),
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT
        )

    async def message(self, query: str) -> Dict[str, Any]:
        """Обработка вопроса пользователя. Возвращает JSON с результатами поиска."""
        result: Dict[str, Any] = await self.agent.ainvoke({
            "messages": [HumanMessage(content=query)]
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
                return {
                    "query": query,
                    "found": False,
                    "fragments": []
                }
            
            print(f"🤖RAG: found={parsed.get('found')}, fragments={len(parsed.get('fragments', []))}")
            return parsed
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Ошибка парсинга JSON от RAG-агента: {e}")
            print(f"Получен ответ: {response[:200]}")
            # Возвращаем пустой результат при ошибке
            return {
                "query": query,
                "found": False,
                "fragments": []
            }

    def __repr__(self) -> str:
        return f"RAGAgent(user_id='{self.user_id}', tools={len(self.tools)})"
