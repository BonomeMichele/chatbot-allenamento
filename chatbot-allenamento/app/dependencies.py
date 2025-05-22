"""
Dipendenze condivise dell'applicazione
"""

from functools import lru_cache
from app.config import settings
from app.core.rag_engine import RAGEngine
from app.core.llm_manager import LLMManager
from app.db.file_storage import FileStorage
from app.services.chat_service import ChatService
from app.services.workout_service import WorkoutService

# Cache per le istanze singleton
_rag_engine = None
_llm_manager = None
_file_storage = None
_chat_service = None
_workout_service = None

@lru_cache()
def get_settings():
    """Ottieni le configurazioni dell'applicazione"""
    return settings

def get_rag_engine() -> RAGEngine:
    """Ottieni l'istanza del motore RAG"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine

def get_llm_manager() -> LLMManager:
    """Ottieni l'istanza del gestore LLM"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager

def get_file_storage() -> FileStorage:
    """Ottieni l'istanza del file storage"""
    global _file_storage
    if _file_storage is None:
        _file_storage = FileStorage()
    return _file_storage

def get_chat_service() -> ChatService:
    """Ottieni l'istanza del servizio chat"""
    global _chat_service
    if _chat_service is None:
        storage = get_file_storage()
        llm = get_llm_manager()
        rag = get_rag_engine()
        _chat_service = ChatService(storage, llm, rag)
    return _chat_service

def get_workout_service() -> WorkoutService:
    """Ottieni l'istanza del servizio workout"""
    global _workout_service
    if _workout_service is None:
        storage = get_file_storage()
        llm = get_llm_manager()
        rag = get_rag_engine()
        _workout_service = WorkoutService(storage, llm, rag)
    return _workout_service
