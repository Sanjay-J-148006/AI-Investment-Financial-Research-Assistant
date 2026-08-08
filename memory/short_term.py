from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

# Store per session_id
_store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Returns or creates an in-memory chat message history for a given session ID.
    """
    if session_id not in _store:
        _store[session_id] = ChatMessageHistory()
    return _store[session_id]

def clear_session_history(session_id: str):
    """
    Clears the chat message history for a session.
    """
    if session_id in _store:
        _store[session_id].clear()
