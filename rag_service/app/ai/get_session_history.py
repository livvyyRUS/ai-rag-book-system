from langchain_core.chat_history import InMemoryChatMessageHistory

store = {}  # словарь для хранения истории в памяти


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


def clear_session_history(session_id: str) -> bool:
    """Очищает историю сообщений конкретного пользователя.
    
    :param session_id: идентификатор пользователя
    :return: True если история была очищена, False если история не найдена
    """
    if session_id in store:
        del store[session_id]
        return True
    return False


def clear_all_history() -> int:
    """Очищает всю историю сообщений всех пользователей.
    
    :return: количество очищенных сессий
    """
    count = len(store)
    store.clear()
    return count
