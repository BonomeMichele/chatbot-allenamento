"""
Test per le API chat
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock

class TestChatAPI:
    """Test per gli endpoint chat"""
    
    def test_send_message_new_chat(self, client: TestClient, mock_chat_service):
        """Test invio messaggio in nuova chat"""
        # Setup mock response
        from tests.conftest import create_mock_chat, create_mock_message
        
        user_msg = create_mock_message("user", "Ciao, come stai?")
        assistant_msg = create_mock_message("assistant", "Ciao! Sto bene, grazie.")
        test_chat = create_mock_chat([user_msg, assistant_msg])
        
        mock_chat_service.send_message = AsyncMock(return_value=(test_chat, user_msg, assistant_msg))
        mock_chat_service.is_workout_request = Mock(return_value=False)
        
        # Test request
        response = client.post("/api/v1/chat/message", json={
            "message": "Ciao, come stai?",
            "chat_id": None
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "chat_id" in data
        assert "title" in data
        assert "user_message" in data
        assert "assistant_message" in data
        
        assert data["user_message"]["content"] == "Ciao, come stai?"
        assert data["assistant_message"]["content"] == "Ciao! Sto bene, grazie."
    
    def test_send_message_workout_request(self, client: TestClient, mock_chat_service, mock_workout_service):
        """Test invio messaggio che richiede una scheda"""
        from tests.conftest import create_mock_chat, create_mock_message
        from app.models.workout import WorkoutPlan, UserProfile, ExperienceLevel, WorkoutGoal
        
        # Setup mock workout
        user_profile = UserProfile(
            experience_level=ExperienceLevel.BEGINNER,
            goals=[WorkoutGoal.GENERAL_FITNESS],
            available_days=3
        )
        
        mock_workout = Mock(spec=WorkoutPlan)
        mock_workout.id = "test-workout"
        mock_workout.title = "Scheda Test"
        mock_workout.user_profile = user_profile
        mock_workout.workout_days = []
        mock_workout.nutrition = None
        mock_workout.progression = None
        mock_workout.general_notes = []
        mock_workout.sources = []
        
        user_msg = create_mock_message("user", "Voglio una scheda di allenamento")
        assistant_msg = create_mock_message("assistant", "Ecco la tua scheda", "workout")
        test_chat = create_mock_chat([user_msg, assistant_msg])
        
        mock_chat_service.is_workout_request = Mock(return_value=True)
        mock_chat_service.send_message = AsyncMock(return_value=(test_chat, user_msg, assistant_msg))
        mock_workout_service.generate_workout_plan = AsyncMock(return_value=mock_workout)
        mock_workout_service.format_workout_for_display = Mock(return_value="Scheda formattata")
        
        response = client.post("/api/v1/chat/message", json={
            "message": "Voglio una scheda di allenamento",
            "chat_id": None
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["assistant_message"]["type"] == "workout"
        mock_workout_service.generate_workout_plan.assert_called_once()
    
    def test_send_message_invalid_input(self, client: TestClient):
        """Test invio messaggio con input non valido"""
        response = client.post("/api/v1/chat/message", json={
            "message": "",  # Messaggio vuoto
            "chat_id": None
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_list_chats(self, client: TestClient, mock_chat_service):
        """Test lista chat"""
        mock_chats = [
            {
                "id": "chat-1",
                "title": "Chat 1",
                "last_message": "Ultimo messaggio",
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00",
                "message_count": 5
            },
            {
                "id": "chat-2", 
                "title": "Chat 2",
                "last_message": "Altro messaggio",
                "created_at": "2024-01-01T13:00:00",
                "updated_at": "2024-01-01T13:00:00",
                "message_count": 3
            }
        ]
        
        mock_chat_service.list_chats = AsyncMock(return_value=mock_chats)
        
        response = client.get("/api/v1/chat/list")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "chats" in data
        assert "total" in data
        assert len(data["chats"]) == 2
        assert data["total"] == 2
        assert data["chats"][0]["id"] == "chat-1"
    
    def test_list_chats_with_limit(self, client: TestClient, mock_chat_service):
        """Test lista chat con limite"""
        mock_chats = [{"id": "chat-1", "title": "Chat 1", "message_count": 1, 
                      "created_at": "2024-01-01T12:00:00", "updated_at": "2024-01-01T12:00:00"}]
        
        mock_chat_service.list_chats = AsyncMock(return_value=mock_chats)
        
        response = client.get("/api/v1/chat/list?limit=1")
        
        assert response.status_code == 200
        mock_chat_service.list_chats.assert_called_with(limit=1)
    
    def test_get_chat_existing(self, client: TestClient, mock_chat_service):
        """Test recupero chat esistente"""
        from tests.conftest import create_mock_chat, create_mock_message
        
        messages = [
            create_mock_message("user", "Ciao"),
            create_mock_message("assistant", "Ciao! Come posso aiutarti?")
        ]
        test_chat = create_mock_chat(messages)
        test_chat.id = "chat-123"
        
        mock_chat_service.get_chat = AsyncMock(return_value=test_chat)
        
        response = client.get("/api/v1/chat/chat-123")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == "chat-123"
        assert "messages" in data
        assert len(data["messages"]) == 2
        
        mock_chat_service.get_chat.assert_called_with("chat-123")
    
    def test_get_chat_not_found(self, client: TestClient, mock_chat_service):
        """Test recupero chat inesistente"""
        mock_chat_service.get_chat = AsyncMock(return_value=None)
        
        response = client.get("/api/v1/chat/nonexistent")
        
        assert response.status_code == 404
    
    def test_update_chat_title(self, client: TestClient, mock_chat_service):
        """Test aggiornamento titolo chat"""
        mock_chat_service.update_chat_title = AsyncMock(return_value=True)
        
        response = client.put("/api/v1/chat/chat-123", json={
            "title": "Nuovo Titolo"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        mock_chat_service.update_chat_title.assert_called_with("chat-123", "Nuovo Titolo")
    
    def test_update_chat_not_found(self, client: TestClient, mock_chat_service):
        """Test aggiornamento chat inesistente"""
        mock_chat_service.update_chat_title = AsyncMock(return_value=False)
        
        response = client.put("/api/v1/chat/nonexistent", json={
            "title": "Nuovo Titolo"
        })
        
        assert response.status_code == 404
    
    def test_delete_chat_existing(self, client: TestClient, mock_chat_service):
        """Test eliminazione chat esistente"""
        mock_chat_service.delete_chat = AsyncMock(return_value=True)
        
        response = client.delete("/api/v1/chat/chat-123")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["deleted_chat_id"] == "chat-123"
        
        mock_chat_service.delete_chat.assert_called_with("chat-123")
    
    def test_delete_chat_not_found(self, client: TestClient, mock_chat_service):
        """Test eliminazione chat inesistente"""
        mock_chat_service.delete_chat = AsyncMock(return_value=False)
        
        response = client.delete("/api/v1/chat/nonexistent")
        
        assert response.status_code == 404
    
    def test_delete_all_chats(self, client: TestClient, mock_chat_service):
        """Test eliminazione tutte le chat"""
        mock_chat_service.delete_all_chats = AsyncMock(return_value=5)
        
        response = client.delete("/api/v1/chat")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["deleted_count"] == 5
        
        mock_chat_service.delete_all_chats.assert_called_once()
    
    def test_get_chat_statistics(self, client: TestClient, mock_chat_service):
        """Test recupero statistiche chat"""
        mock_stats = {
            "total_chats": 10,
            "total_messages": 50,
            "average_messages_per_chat": 5.0,
            "most_recent": {"id": "chat-latest", "created_at": "2024-01-01T12:00:00"},
            "oldest": {"id": "chat-oldest", "created_at": "2023-12-01T12:00:00"}
        }
        
        mock_chat_service.get_chat_statistics = AsyncMock(return_value=mock_stats)
        
        response = client.get("/api/v1/chat/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_chats"] == 10
        assert data["total_messages"] == 50
        assert data["average_messages_per_chat"] == 5.0
