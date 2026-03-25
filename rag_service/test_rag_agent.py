import asyncio
from app.ai.agents.rag_agent import RAGAgent

async def test_rag_agent():
    user_id = "test"
    query = "Почему Раскольников решает убить старуху-процентщицу?"
    
    print(f"🧪 Тест RAG-агента для user_id={user_id}")
    print(f"🧪 Запрос: {query}")
    print("=" * 80)
    
    agent = RAGAgent(user_id=user_id)
    result = await agent.message(query=query)
    
    print("=" * 80)
    print(f"🧪 Результат:")
    print(f"  found: {result.get('found')}")
    print(f"  fragments: {len(result.get('fragments', []))}")
    print(f"  query: {result.get('query')}")
    
    if result.get('fragments'):
        print(f"\n🧪 Фрагменты:")
        for i, frag in enumerate(result['fragments'], 1):
            print(f"  [{i}] {frag.get('book')} (стр. {frag.get('location')})")
            print(f"      {frag.get('text')[:100]}...")

if __name__ == "__main__":
    asyncio.run(test_rag_agent())
