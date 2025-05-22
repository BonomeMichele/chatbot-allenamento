"""
Test per le API workout
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock

class TestWorkoutAPI:
    """Test per gli endpoint workout"""
    
    def test_generate_workout_success(self, client: TestClient, mock_workout_service, sample_user_request):
        """Test generazione scheda con successo"""
        from app.models.workout import WorkoutPlan, UserProfile, ExperienceLevel, WorkoutGoal
        
        # Setup mock workout
        user_profile = UserProfile(
            age=25,
            experience_level=ExperienceLevel.BEGINNER,
            goals=[WorkoutGoal.GENERAL_FITNESS],
            available_days=3
        )
        
        mock_workout = Mock(spec=WorkoutPlan)
        mock_workout.id = "test-workout-123"
        mock_workout.title = "Scheda Principiante"
        mock_workout.user_profile = user_profile
        mock_workout.workout_days = []
        mock_workout.nutrition = None
        mock_workout.progression = None
        mock_workout.general_notes = ["Nota di test"]
        mock_workout.sources = ["test.pdf"]
        mock_workout.created_at = "2024-01-01T12:00:00"
        
        mock_workout_service.generate_workout_plan = AsyncMock(return_value=mock_workout)
        
        response = client.post("/api/v1/workout/generate", json=sample_user_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["workout_plan"] is not None
        assert data["workout_plan"]["id"] == "test-workout-123"
        assert data["workout_plan"]["title"] == "Scheda Principiante"
        assert data["message"] == "Scheda di allenamento generata con successo!"
        
        mock_workout_service.generate_workout_plan.assert_called_once()
    
    def test_generate_workout_invalid_input(self, client: TestClient):
        """Test generazione scheda con input non valido"""
        response = client.post("/api/v1/workout/generate", json={
            "user_input": "",  # Input vuoto
            "chat_id": None
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_generate_workout_service_error(self, client: TestClient, mock_workout_service):
        """Test generazione scheda con errore del servizio"""
        mock_workout_service.generate_workout_plan = AsyncMock(
            side_effect=Exception("Errore del servizio")
        )
        
        response = client.post("/api/v1/workout/generate", json={
            "user_input": "Voglio una scheda di allenamento",
            "chat_id": None
        })
        
        assert response.status_code == 200  # L'API gestisce l'errore
        data = response.json()
        
        assert data["success"] is False
        assert "Errore nella generazione della scheda" in data["message"]
        assert data["workout_plan"] is None
    
    def test_list_workouts_empty(self, client: TestClient, mock_workout_service):
        """Test lista schede vuota"""
        mock_workout_service.list_workout_plans = AsyncMock(return_value=[])
        
        response = client.get("/api/v1/workout/list")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "workouts" in data
        assert "total" in data
        assert len(data["workouts"]) == 0
        assert data["total"] == 0
    
    def test_list_workouts_with_data(self, client: TestClient, mock_workout_service):
        """Test lista schede con dati"""
        mock_workouts = [
            {
                "id": "workout-1",
                "title": "Scheda 1",
                "created_at": "2024-01-01T12:00:00",
                "total_days": 3,
                "total_exercises": 9
            },
            {
                "id": "workout-2",
                "title": "Scheda 2", 
                "created_at": "2024-01-02T12:00:00",
                "total_days": 4,
                "total_exercises": 12
            }
        ]
        
        mock_workout_service.list_workout_plans = AsyncMock(return_value=mock_workouts)
        
        response = client.get("/api/v1/workout/list")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["workouts"]) == 2
        assert data["total"] == 2
        assert data["workouts"][0]["id"] == "workout-1"
        assert data["workouts"][1]["id"] == "workout-2"
    
    def test_list_workouts_with_limit(self, client: TestClient, mock_workout_service):
        """Test lista schede con limite"""
        mock_workouts = [
            {
                "id": "workout-1",
                "title": "Scheda 1",
                "created_at": "2024-01-01T12:00:00",
                "total_days": 3,
                "total_exercises": 9
            }
        ]
        
        mock_workout_service.list_workout_plans = AsyncMock(return_value=mock_workouts)
        
        response = client.get("/api/v1/workout/list?limit=1")
        
        assert response.status_code == 200
        mock_workout_service.list_workout_plans.assert_called_with(limit=1)
    
    def test_get_workout_existing(self, client: TestClient, mock_workout_service, sample_workout_data):
        """Test recupero scheda esistente"""
        from app.models.workout import WorkoutPlan
        
        mock_workout = WorkoutPlan(**sample_workout_data)
        mock_workout_service.get_workout_plan = AsyncMock(return_value=mock_workout)
        
        response = client.get("/api/v1/workout/test-workout-123")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == "test-workout-123"
        assert data["title"] == "Scheda Principiante"
        assert "workout_days" in data
        assert len(data["workout_days"]) == 1
        
        mock_workout_service.get_workout_plan.assert_called_with("test-workout-123")
    
    def test_get_workout_not_found(self, client: TestClient, mock_workout_service):
        """Test recupero scheda inesistente"""
        mock_workout_service.get_workout_plan = AsyncMock(return_value=None)
        
        response = client.get("/api/v1/workout/nonexistent")
        
        assert response.status_code == 404
    
    def test_delete_workout_existing(self, client: TestClient, mock_workout_service):
        """Test eliminazione scheda esistente"""
        mock_workout_service.delete_workout_plan = AsyncMock(return_value=True)
        
        response = client.delete("/api/v1/workout/workout-123")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["deleted_workout_id"] == "workout-123"
        assert data["message"] == "Scheda di allenamento eliminata con successo"
        
        mock_workout_service.delete_workout_plan.assert_called_with("workout-123")
    
    def test_delete_workout_not_found(self, client: TestClient, mock_workout_service):
        """Test eliminazione scheda inesistente"""
        mock_workout_service.delete_workout_plan = AsyncMock(return_value=False)
        
        response = client.delete("/api/v1/workout/nonexistent")
        
        assert response.status_code == 404
    
    def test_create_workout_variation(self, client: TestClient, mock_workout_service):
        """Test creazione variazione scheda"""
        from app.models.workout import WorkoutPlan, UserProfile, ExperienceLevel, WorkoutGoal
        
        # Setup mock variation
        user_profile = UserProfile(
            experience_level=ExperienceLevel.INTERMEDIATE,
            goals=[WorkoutGoal.STRENGTH],
            available_days=4
        )
        
        mock_variation = Mock(spec=WorkoutPlan)
        mock_variation.id = "variation-123"
        mock_variation.title = "Scheda Intermedio - Variazione harder"
        mock_variation.user_profile = user_profile
        mock_variation.workout_days = []
        mock_variation.nutrition = None
        mock_variation.progression = None
        mock_variation.general_notes = []
        mock_variation.sources = []
        mock_variation.created_at = "2024-01-01T12:00:00"
        
        mock_workout_service.generate_workout_variations = AsyncMock(return_value=mock_variation)
        
        response = client.post("/api/v1/workout/base-workout-123/variations?variation_type=harder")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["workout_plan"]["id"] == "variation-123"
        assert "harder" in data["message"]
        
        mock_workout_service.generate_workout_variations.assert_called_with(
            base_workout_id="base-workout-123",
            variation_type="harder"
        )
    
    def test_get_workout_recommendations(self, client: TestClient, mock_workout_service):
        """Test recupero raccomandazioni schede"""
        mock_recommendations = [
            {
                "name": "Scheda Full Body",
                "description": "Perfetta per principianti",
                "days": 3,
                "focus": "Divisione corpo",
                "benefits": "Maggiore volume"
            }
        ]
        
        mock_workout_service.get_workout_recommendations = AsyncMock(return_value=mock_recommendations)
        
        response = client.get("/api/v1/workout/recommendations?goals=forza&goals=ipertrofia&experience_level=intermedio")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["recommendations"]) == 2
        assert data["recommendations"][0]["name"] == "Scheda Full Body"
        
        mock_workflow_service.get_workout_recommendations.assert_called_with(
            user_goals=["forza", "ipertrofia"],
            experience_level="intermedio"
        )
    
    def test_workout_generation_with_overrides(self, client: TestClient, mock_workout_service):
        """Test generazione scheda con parametri override"""
        from app.models.workout import WorkoutPlan, UserProfile, ExperienceLevel, WorkoutGoal
        
        user_profile = UserProfile(
            age=30,
            experience_level=ExperienceLevel.INTERMEDIATE,
            goals=[WorkoutGoal.STRENGTH],
            available_days=4
        )
        
        mock_workout = Mock(spec=WorkoutPlan)
        mock_workout.id = "override-workout"
        mock_workout.title = "Scheda Forza"
        mock_workout.user_profile = user_profile
        mock_workout.workout_days = []
        mock_workout.nutrition = None
        mock_workout.progression = None
        mock_workout.general_notes = []
        mock_workout.sources = []
        mock_workout.created_at = "2024-01-01T12:00:00"
        
        mock_workout_service.generate_workout_plan = AsyncMock(return_value=mock_workout)
        
        request_data = {
            "user_input": "Voglio aumentare la forza",
            "chat_id": None,
            "age": 30,
            "experience_level": "intermedio",
            "available_days": 4,
            "goals": ["forza"]
        }
        
        response = client.post("/api/v1/workout/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        mock_workout_service.generate_workout_plan.assert_called_once()
    
    def test_workout_api_error_handling(self, client: TestClient, mock_workout_service):
        """Test gestione errori API workout"""
        # Test timeout/connection error
        mock_workout_service.generate_workout_plan = AsyncMock(
            side_effect=TimeoutError("Timeout nella generazione")
        )
        
        response = client.post("/api/v1/workout/generate", json={
            "user_input": "Scheda di test",
            "chat_id": None
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Errore nella generazione della scheda" in data["message"]Corpo completo",
                "benefits": "Sviluppo equilibrato"
            },
            {
                "name": "Scheda Upper/Lower",
                "description": "Ideale per intermedi",
                "days": 4,
                "focus": "
