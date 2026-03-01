from langchain_core.chat_history import InMemoryChatMessageHistory

store = {}  # словарь для хранения истории в памяти


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]
