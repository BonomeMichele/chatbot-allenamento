"""
Test per WorkoutGenerator
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock
from app.core.workout_generator import WorkoutGenerator
from app.models.workout import UserProfile, ExperienceLevel, WorkoutGoal
from app.core.error_handler import ChatbotException

class TestWorkoutGenerator:
    """Test per il generatore di schede"""
    
    @pytest.fixture
    def workout_generator(self, mock_llm_manager, mock_rag_engine):
        """Fixture per WorkoutGenerator"""
        return WorkoutGenerator(mock_llm_manager, mock_rag_engine)
    
    @pytest.fixture
    def sample_user_profile(self):
        """Profilo utente di esempio"""
        return UserProfile(
            age=25,
            experience_level=ExperienceLevel.BEGINNER,
            goals=[WorkoutGoal.GENERAL_FITNESS],
            available_days=3,
            injuries=[],
            equipment=["bilanciere", "manubri"],
            preferences=[]
        )
    
    @pytest.mark.asyncio
    async def test_generate_complete_workout_success(self, workout_generator, sample_user_profile):
        """Test generazione scheda completa con successo"""
        # Setup mocks
        workout_generator.rag_engine.retrieve_context = AsyncMock(
            return_value=("Contesto test", ["source1.pdf"])
        )
        
        # Mock per struttura workout
        structure_response = {
            "title": "Scheda Principiante",
            "split_type": "full_body",
            "days_structure": [
                {
                    "day": "Lunedì",
                    "focus": "Corpo completo",
                    "muscle_groups": ["petto", "schiena"],
                    "workout_type": "mixed"
                }
            ],
            "session_duration": 60,
            "weekly_volume": "medio"
        }
        
        # Mock per esercizi
        exercises_response = {
            "warm_up": ["Riscaldamento 5 min"],
            "exercises": [
                {
                    "name": "Squat",
                    "sets": 3,
                    "reps": "12-15",
                    "rest": "90 sec",
                    "weight": "Corpo libero",
                    "notes": "Mantieni schiena dritta",
                    "muscle_groups": ["quadricipiti", "glutei"]
                }
            ],
            "cool_down": ["Stretching"]
        }
        
        workout_generator.llm_manager.generate_response = AsyncMock(
            side_effect=[
                json.dumps(structure_response),  # Prima chiamata per struttura
                json.dumps(exercises_response),  # Seconda chiamata per esercizi
                json.dumps({  # Nutrizione
                    "calories_estimate": "2000 kcal",
                    "protein_grams": "100g",
                    "meal_timing": ["Colazione ricca"],
                    "hydration": "2.5L",
                    "supplements": ["Proteine"]
                }),
                json.dumps({  # Progressione
                    "week_1_2": "Apprendimento tecnica",
                    "week_3_4": "Aumento ripetizioni",
                    "progression_notes": ["Progredisci gradualmente"]
                })
            ]
        )
        
        # Test
        workout_plan = await workout_generator.generate_complete_workout(
            sample_user_profile, 
            "Voglio iniziare ad allenarmi"
        )
        
        # Assertions
        assert workout_plan is not None
        assert workout_plan.title == "Scheda Principiante - Fitness"
        assert len(workout_plan.workout_days) == 1
        assert workout_plan.workout_days[0].day == "Lunedì"
        assert len(workout_plan.workout_days[0].exercises) == 1
        assert workout_plan.workout_days[0].exercises[0].name == "Squat"
        assert workout_plan.nutrition is not None
        assert workout_plan.progression is not None
        assert "source1.pdf" in workout_plan.sources
    
    @pytest.mark.asyncio
    async def test_get_relevant_context_beginner(self, workout_generator, sample_user_profile):
        """Test recupero contesto per principiante"""
        workout_generator.rag_engine.retrieve_context = AsyncMock(
            return_value=("Contesto principiante", ["beginner.pdf"])
        )
        
        context, sources = await workout_generator._get_relevant_context(sample_user_profile)
        
        assert "Contesto principiante" == context
        assert "beginner.pdf" in sources
        
        # Verifica che la query contenga elementi del profilo
        call_args = workout_generator.rag_engine.retrieve_context.call_args[0]
        query = call_args[0]
        assert "principiante" in query
        assert "fitness_generale" in query
    
    @pytest.mark.asyncio
    async def test_get_relevant_context_advanced_split(self, workout_generator):
        """Test recupero contesto per utente avanzato con molti giorni"""
        advanced_profile = UserProfile(
            experience_level=ExperienceLevel.ADVANCED,
            goals=[WorkoutGoal.STRENGTH],
            available_days=5,
            injuries=["spalla"]
        )
        
        workout_generator.rag_engine.retrieve_context = AsyncMock(
            return_value=("Contesto avanzato", ["advanced.pdf"])
        )
        
        context, sources = await workout_generator._get_relevant_context(advanced_profile)
        
        call_args = workout_generator.rag_engine.retrieve_context.call_args[0]
        query = call_args[0]
        assert "avanzato" in query
        assert "forza" in query
        assert "split routine" in query
        assert "spalla" in query
    
    @pytest.mark.asyncio
    async def test_generate_workout_structure_json_response(self, workout_generator, sample_user_profile):
        """Test generazione struttura con risposta JSON valida"""
        valid_structure = {
            "title": "Test Workout",
            "split_type": "full_body",
            "days_structure": [
                {
                    "day": "Lunedì",
                    "focus": "Test focus",
                    "muscle_groups": ["test"],
                    "workout_type": "mixed"
                }
            ]
        }
        
        workout_generator.llm_manager.generate_response = AsyncMock(
            return_value=json.dumps(valid_structure)
        )
        
        result = await workout_generator._generate_workout_structure(
            sample_user_profile, "test input", "test context"
        )
        
        assert result == valid_structure
        assert result["title"] == "Test Workout"
    
    @pytest.mark.asyncio
    async def test_generate_workout_structure_invalid_json(self, workout_generator, sample_user_profile):
        """Test generazione struttura con JSON non valido"""
        workout_generator.llm_manager.generate_response = AsyncMock(
            return_value="Invalid JSON response"
        )
        
        result = await workout_generator._generate_workout_structure(
            sample_user_profile, "test input", "test context"
        )
        
        # Dovrebbe restituire struttura di default
        assert "days_structure" in result
        assert len(result["days_structure"]) <= sample_user_profile.available_days
    
    @pytest.mark.asyncio
    async def test_generate_detailed_exercises_success(self, workout_generator, sample_user_profile):
        """Test generazione esercizi dettagliati"""
        structure = {
            "days_structure": [
                {
                    "day": "Lunedì",
                    "focus": "Corpo completo",
                    "muscle_groups": ["petto", "schiena"],
                    "workout_type": "mixed"
                }
            ],
            "session_duration": 60
        }
        
        exercises_response = {
            "warm_up": ["Camminata 5 min"],
            "exercises": [
                {
                    "name": "Push-up",
                    "sets": 3,
                    "reps": "10-12",
                    "rest": "60 sec",
                    "weight": "Corpo libero",
                    "notes": "Mantieni corpo dritto",
                    "muscle_groups": ["pettorali"]
                }
            ],
            "cool_down": ["Stretching petto"]
        }
        
        workout_generator.llm_manager.generate_response = AsyncMock(
            return_value=json.dumps(exercises_response)
        )
        
        workout_days = await workout_generator._generate_detailed_exercises(
            structure, sample_user_profile, "test context"
        )
        
        assert len(workout_days) == 1
        assert workout_days[0].day == "Lunedì"
        assert len(workout_days[0].exercises) == 1
        assert workout_days[0].exercises[0].name == "Push-up"
        assert workout_days[0].exercises[0].sets == 3
        assert "Camminata 5 min" in workout_days[0].warm_up
        assert "Stretching petto" in workout_days[0].cool_down
    
    @pytest.mark.asyncio
    async def test_generate_nutrition_guidelines_weight_loss(self, workout_generator):
        """Test generazione linee guida nutrizionali per dimagrimento"""
        weight_loss_profile = UserProfile(
            experience_level=ExperienceLevel.BEGINNER,
            goals=[WorkoutGoal.WEIGHT_LOSS],
            available_days=3
        )
        
        nutrition_response = {
            "calories_estimate": "1800-2000 kcal",
            "protein_grams": "120-140g",
            "meal_timing": ["Colazione abbondante", "Cena leggera"],
            "hydration": "3L acqua",
            "supplements": ["Multivitaminico"]
        }
        
        workout_generator.llm_manager.generate_response = AsyncMock(
            return_value=json.dumps(nutrition_response)
        )
        
        nutrition = await workout_generator._generate_nutrition_guidelines(
            weight_loss_profile, "test context"
        )
        
        assert nutrition is not None
        assert nutrition.calories_estimate == "1800-2000 kcal"
        assert nutrition.protein_grams == "120-140g"
        assert "Colazione abbondante" in nutrition.meal_timing
        assert nutrition.hydration == "3L acqua"
        assert "Multivitaminico" in nutrition.supplements
    
    @pytest.mark.asyncio
    async def test_generate_nutrition_guidelines_general_fitness(self, workout_generator, sample_user_profile):
        """Test che non genera nutrizione per fitness generale"""
        nutrition = await workout_generator._generate_nutrition_guidelines(
            sample_user_profile, "test context"
        )
        
        assert nutrition is None
    
    @pytest.mark.asyncio
    async def test_generate_progression_plan_success(self, workout_generator, sample_user_profile):
        """Test generazione piano di progressione"""
        progression_response = {
            "week_1_2": "Apprendimento base",
            "week_3_4": "Aumento volume",
            "week_5_6": "Intensificazione",
            "deload_week": "Scarico attivo",
            "progression_notes": ["Nota 1", "Nota 2"]
        }
        
        workout_generator.llm_manager.generate_response = AsyncMock(
            return_value=json.dumps(progression_response)
        )
        
        progression = await workout_generator._generate_progression_plan(
            sample_user_profile, "test context"
        )
        
        assert progression is not None
        assert progression.week_1_2 == "Apprendimento base"
        assert progression.week_3_4 == "Aumento volume"
        assert progression.week_5_6 == "Intensificazione"
        assert progression.deload_week == "Scarico attivo"
        assert len(progression.progression_notes) == 2
    
    def test_generate_title_single_goal(self, workout_generator):
        """Test generazione titolo con singolo obiettivo"""
        profile = UserProfile(
            experience_level=ExperienceLevel.INTERMEDIATE,
            goals=[WorkoutGoal.STRENGTH],
            available_days=4
        )
        
        title = workout_generator._generate_title(profile)
        assert title == "Scheda Intermedio - Forza"
    
    def test_generate_title_multiple_goals(self, workout_generator):
        """Test generazione titolo con obiettivi multipli"""
        profile = UserProfile(
            experience_level=ExperienceLevel.ADVANCED,
            goals=[WorkoutGoal.STRENGTH, WorkoutGoal.HYPERTROPHY],
            available_days=5
        )
        
        title = workout_generator._generate_title(profile)
        assert title == "Scheda Avanzato - 5 giorni"
    
    def test_generate_general_notes_beginner(self, workout_generator, sample_user_profile):
        """Test generazione note per principiante"""
        notes = workout_generator._generate_general_notes(sample_user_profile)
        
        assert len(notes) > 4  # Note base + note per principianti
        assert any("principiante" in note.lower() for note in notes)
        assert any("tecnica" in note.lower() for note in notes)
        assert any("riscaldamento" in note.lower() for note in notes)
    
    def test_generate_general_notes_with_injuries(self, workout_generator):
        """Test generazione note con infortuni"""
        profile = UserProfile(
            experience_level=ExperienceLevel.INTERMEDIATE,
            goals=[WorkoutGoal.GENERAL_FITNESS],
            available_days=3,
            injuries=["ginocchio"]
        )
        
        notes = workout_generator._generate_general_notes(profile)
        
        assert any("infortuni" in note.lower() for note in notes)
    
    def test_generate_general_notes_strength_goal(self, workout_generator):
        """Test generazione note per obiettivo forza"""
        profile = UserProfile(
            experience_level=ExperienceLevel.INTERMEDIATE,
            goals=[WorkoutGoal.STRENGTH],
            available_days=4
        )
        
        notes = workout_generator._generate_general_notes(profile)
        
        assert any("forza" in note.lower() for note in notes)
        assert any("carico" in note.lower() or "recupero" in note.lower() for note in notes)
    
    @pytest.mark.asyncio
    async def test_error_handling_in_generation(self, workout_generator, sample_user_profile):
        """Test gestione errori durante la generazione"""
        workout_generator.rag_engine.retrieve_context = AsyncMock(
            side_effect=Exception("RAG Error")
        )
        
        with pytest.raises(ChatbotException) as exc_info:
            await workout_generator.generate_complete_workout(
                sample_user_profile, "test input"
            )
        
        assert "Errore nella generazione della scheda" in str(exc_info.value)
