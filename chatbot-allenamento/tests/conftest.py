"""
Configurazioni pytest per i test
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import (
    get_rag_engine, get_llm_manager, get_file_storage,
    get_chat_service, get_workout_service
)
from app.core.rag_engine import RAGEngine
from app.core.llm_manager import LLMManager
from app.db.file_storage import FileStorage
from app.services.chat_service import ChatService
from app.services.workout_service import WorkoutService

@pytest.fixture(scope="session")
def event_loop():
    """Crea un event loop per i test asincroni"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_dir():
    """Crea una directory temporanea per i test"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def mock_openai_response():
    """Mock per le risposte OpenAI"""
    return {
        "choices": [{
            "message": {
                "content": "Risposta di test dall'AI"
            }
        }]
    }

@pytest.fixture
def mock_llm_manager():
    """Mock per LLMManager"""
    mock = Mock(spec=LLMManager)
    mock.generate_response = AsyncMock(return_value="Risposta di test")
    mock.generate_workout_response = AsyncMock(return_value="Scheda di test")
    mock.generate_chat_response = AsyncMock(return_value="Chat di test")
    mock.extract_user_profile = AsyncMock(return_value={
        "age": 25,
        "gender": "maschio",
        "experience_level": "principiante",
        "goals": ["fitness_generale"],
        "available_days": 3,
        "injuries": [],
        "equipment": [],
        "preferences": []
    })
    mock.is_available = Mock(return_value=True)
    return mock

@pytest.fixture
def mock_rag_engine():
    """Mock per RAGEngine"""
    mock = Mock(spec=RAGEngine)
    mock.retrieve_context = AsyncMock(return_value=(
        "Contesto di test dal RAG",
        ["fonte1.pdf", "fonte2.pdf"]
    ))
    mock.search_documents = AsyncMock(return_value=[
        {
            "text": "Testo di test",
            "metadata": {"source": "test.pdf"},
            "score": 0.9
        }
    ])
    mock.is_initialized = Mock(return_value=True)
    mock.initialize = AsyncMock()
    return mock

@pytest.fixture
def mock_file_storage(temp_dir):
    """Mock per FileStorage con directory temporanea"""
    mock = Mock(spec=FileStorage)
    
    # Simula storage su file system temporaneo
    mock.chats_path = temp_dir / "chats"
    mock.workouts_path = temp_dir / "workouts"
    mock.chats_path.mkdir(exist_ok=True)
    mock.workouts_path.mkdir(exist_ok=True)
    
    # Mock methods
    mock.save_chat = Mock()
    mock.load_chat = Mock(return_value=None)
    mock.list_chats = Mock(return_value=[])
    mock.delete_chat = Mock(return_value=True)
    mock.delete_all_chats = Mock(return_value=0)
    
    mock.save_workout = Mock()
    mock.load_workout = Mock(return_value=None)
    mock.list_workouts = Mock(return_value=[])
    mock.delete_workout = Mock(return_value=True)
    
    return mock

@pytest.fixture
def mock_chat_service(mock_file_storage, mock_llm_manager, mock_rag_engine):
    """Mock per ChatService"""
    return ChatService(mock_file_storage, mock_llm_manager, mock_rag_engine)

@pytest.fixture
def mock_workout_service(mock_file_storage, mock_llm_manager, mock_rag_engine):
    """Mock per WorkoutService"""
    return WorkoutService(mock_file_storage, mock_llm_manager, mock_rag_engine)

@pytest.fixture
def client(mock_rag_engine, mock_llm_manager, mock_file_storage, 
           mock_chat_service, mock_workout_service):
    """Client di test FastAPI con dipendenze mockate"""
    
    # Override delle dipendenze
    app.dependency_overrides[get_rag_engine] = lambda: mock_rag_engine
    app.dependency_overrides[get_llm_manager] = lambda: mock_llm_manager
    app.dependency_overrides[get_file_storage] = lambda: mock_file_storage
    app.dependency_overrides[get_chat_service] = lambda: mock_chat_service
    app.dependency_overrides[get_workout_service] = lambda: mock_workout_service
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Pulisce le override
    app.dependency_overrides.clear()

@pytest.fixture
def sample_chat_data():
    """Dati di esempio per una chat"""
    return {
        "id": "test-chat-123",
        "title": "Chat di Test",
        "messages": [
            {
                "id": "msg-1",
                "role": "user",
                "content": "Ciao, voglio una scheda di allenamento",
                "type": "text",
                "timestamp": "2024-01-01T12:00:00",
                "sources": None,
                "metadata": None
            },
            {
                "id": "msg-2", 
                "role": "assistant",
                "content": "Certo! Dimmi i tuoi obiettivi...",
                "type": "text",
                "timestamp": "2024-01-01T12:00:30",
                "sources": ["fonte1.pdf"],
                "metadata": None
            }
        ],
        "status": "active",
        "created_at": "2024-01-01T12:00:00",
        "updated_at": "2024-01-01T12:00:30",
        "user_id": None,
        "metadata": None
    }

@pytest.fixture
def sample_workout_data():
    """Dati di esempio per una scheda di allenamento"""
    return {
        "id": "test-workout-123",
        "title": "Scheda Principiante",
        "user_profile": {
            "age": 25,
            "gender": "maschio",
            "experience_level": "principiante",
            "goals": ["fitness_generale"],
            "available_days": 3,
            "session_duration": 60,
            "injuries": [],
            "equipment": ["bilanciere", "manubri"],
            "preferences": []
        },
        "workout_days": [
            {
                "day": "Lunedì",
                "focus": "Corpo completo",
                "warm_up": ["Camminata 5 min", "Mobilità articolare"],
                "exercises": [
                    {
                        "name": "Squat",
                        "sets": 3,
                        "reps": "12-15",
                        "rest": "90 sec",
                        "weight": "Peso corporeo",
                        "notes": "Mantieni la schiena dritta",
                        "muscle_groups": ["quadricipiti", "glutei"]
                    },
                    {
                        "name": "Push-up",
                        "sets": 3,
                        "reps": "8-12",
                        "rest": "60 sec",
                        "weight": None,
                        "notes": "Su ginocchia se necessario",
                        "muscle_groups": ["pettorali", "tricipiti"]
                    }
                ],
                "cool_down": ["Stretching statico", "Respirazione"],
                "duration_minutes": 45
            }
        ],
        "nutrition": {
            "calories_estimate": "2000-2200 kcal/giorno",
            "protein_grams": "100-120g/giorno",
            "meal_timing": [
                "Colazione ricca in proteine",
                "Spuntino pre-workout",
                "Pasto post-workout entro 2 ore"
            ],
            "hydration": "2.5-3 litri/giorno",
            "supplements": ["Proteine whey", "Creatina"]
        },
        "progression": {
            "week_1_2": "Focus sulla tecnica",
            "week_3_4": "Aumenta ripetizioni",
            "week_5_6": "Aggiungi peso leggero",
            "deload_week": "Riduci volume 30%",
            "progression_notes": ["Progredisci gradualmente", "Ascolta il tuo corpo"]
        },
        "general_notes": [
            "Inizia sempre con riscaldamento",
            "Mantieni forma corretta",
            "Riposa adeguatamente"
        ],
        "sources": ["linee_guida_aci.pdf", "exercises.pdf"],
        "created_at": "2024-01-01T12:00:00",
        "metadata": None
    }

@pytest.fixture
def sample_user_request():
    """Richiesta di esempio per generazione scheda"""
    return {
        "user_input": "Sono un uomo di 25 anni, principiante, voglio allenarmi 3 volte a settimana per migliorare la forma fisica",
        "chat_id": None,
        "age": 25,
        "experience_level": "principiante",
        "available_days": 3,
        "goals": ["fitness_generale"]
    }

@pytest.fixture
async def async_client(client):
    """Client asincrono per test async"""
    return client

# Utility functions per i test
def create_mock_document(content: str, metadata: dict = None):
    """Crea un documento mock per i test RAG"""
    from llama_index.core import Document
    
    return Document(
        text=content,
        metadata=metadata or {"source": "test.pdf"}
    )

def create_mock_message(role: str, content: str, msg_type: str = "text"):
    """Crea un messaggio mock per i test"""
    from app.models.chat import Message, MessageRole, MessageType
    import uuid
    from datetime import datetime
    
    return Message(
        id=str(uuid.uuid4()),
        role=MessageRole(role),
        content=content,
        type=MessageType(msg_type),
        timestamp=datetime.now()
    )

def create_mock_chat(messages: list = None):
    """Crea una chat mock per i test"""
    from app.models.chat import Chat
    import uuid
    from datetime import datetime
    
    return Chat(
        id=str(uuid.uuid4()),
        title="Test Chat",
        messages=messages or [],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
