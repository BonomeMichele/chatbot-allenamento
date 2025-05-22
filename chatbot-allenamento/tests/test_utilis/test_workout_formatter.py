"""
Test per WorkoutFormatter
"""

import pytest
from app.utils.workout_formatter import WorkoutFormatter
from app.models.workout import WorkoutPlan, WorkoutDay, Exercise, UserProfile, ExperienceLevel, WorkoutGoal

class TestWorkoutFormatter:
    """Test per il formattatore di schede"""
    
    @pytest.fixture
    def sample_workout_plan(self, sample_workout_data):
        """Fixture per WorkoutPlan"""
        return WorkoutPlan(**sample_workout_data)
    
    def test_format_for_chat_complete(self, sample_workout_plan):
        """Test formattazione per chat completa"""
        formatted = WorkoutFormatter.format_for_chat(sample_workout_plan)
        
        assert isinstance(formatted, str)
        assert '<div class="workout-card">' in formatted
        assert sample_workout_plan.title in formatted
        assert "👤 Il Tuo Profilo" in formatted
        assert "📅 Lunedì - Corpo completo" in formatted
        assert "💪 Esercizi Principali" in formatted
        assert '<table class="exercise-table">' in formatted
        assert "Squat" in formatted
        assert "Push-up" in formatted
    
    def test_format_for_chat_with_profile(self, sample_workout_plan):
        """Test formattazione sezione profilo"""
        formatted = WorkoutFormatter.format_for_chat(sample_workout_plan)
        
        # Verifica elementi del profilo
        assert "25 anni" in formatted
        assert "maschio" in formatted or "Maschio" in formatted
        assert "principiante" in formatted or "Principiante" in formatted
        assert "fitness_generale" in formatted or "Fitness Generale" in formatted
        assert "3" in formatted  # giorni disponibili
    
    def test_format_for_chat_with_nutrition(self, sample_workout_plan):
        """Test formattazione sezione nutrizione"""
        formatted = WorkoutFormatter.format_for_chat(sample_workout_plan)
        
        assert "🥗 Linee Guida Nutrizionali" in formatted
        assert "2000-2200 kcal/giorno" in formatted
        assert "100-120g/giorno" in formatted
        assert "2.5-3 litri/giorno" in formatted
        assert "Proteine whey" in formatted
        assert "Creatina" in formatted
    
    def test_format_for_chat_with_progression(self, sample_workout_plan):
        """Test formattazione sezione progressione"""
        formatted = WorkoutFormatter.format_for_chat(sample_workout_plan)
        
        assert "📈 Piano di Progressione" in formatted
        assert "Focus sulla tecnica" in formatted
        assert "Aumenta ripetizioni" in formatted
        assert "Aggiungi peso leggero" in formatted
        assert "Riduci volume 30%" in formatted
    
    def test_format_for_chat_with_notes(self, sample_workout_plan):
        """Test formattazione note generali"""
        formatted = WorkoutFormatter.format_for_chat(sample_workout_plan)
        
        assert "📝 Note Importanti" in formatted
        assert "Inizia sempre con riscaldamento" in formatted
        assert "Mantieni forma corretta" in formatted
        assert "Riposa adeguatamente" in formatted
    
    def test_format_exercises_table_complete(self):
        """Test formattazione tabella esercizi completa"""
        exercises = [
            Exercise(
                name="Squat",
                sets=3,
                reps="12-15",
                rest="90 sec",
                weight="Peso corporeo",
                notes="Mantieni schiena dritta",
                muscle_groups=["quadricipiti", "glutei"]
            ),
            Exercise(
                name="Push-up",
                sets=3,
                reps="8-12",
                rest="60 sec",
                weight=None,
                notes=None,
                muscle_groups=["pettorali"]
            )
        ]
        
        table_html = WorkoutFormatter._format_exercises_table(exercises)
        
        assert '<table class="exercise-table">' in table_html
        assert "<thead>" in table_html
        assert "<tbody>" in table_html
        assert "Esercizio" in table_html
        assert "Serie" in table_html
        assert "Ripetizioni" in table_html
        assert "Recupero" in table_html
        assert "Peso" in table_html  # Perché c'è almeno un esercizio con peso
        
        # Verifica contenuto righe
        assert "<strong>Squat</strong>" in table_html
        assert "12-15" in table_html
        assert "90 sec" in table_html
        assert "Peso corporeo" in table_html
        assert "Mantieni schiena dritta" in table_html
        assert "🎯 quadricipiti, glutei" in table_html
        
        assert "<strong>Push-up</strong>" in table_html
        assert "8-12" in table_html
        assert "60 sec" in table_html
        assert "🎯 pettorali" in table_html
    
    def test_format_exercises_table_no_weights(self):
        """Test formattazione tabella senza pesi"""
        exercises = [
            Exercise(
                name="Plank",
                sets=3,
                reps="30 sec",
                rest="60 sec",
                muscle_groups=["core"]
            )
        ]
        
        table_html = WorkoutFormatter._format_exercises_table(exercises)
        
        # Non dovrebbe includere colonna peso
        header_count = table_html.count("<th>")
        assert header_count == 4  # Esercizio, Serie, Ripetizioni, Recupero (no Peso)
    
    def test_format_exercises_table_empty(self):
        """Test formattazione tabella vuota"""
        table_html = WorkoutFormatter._format_exercises_table([])
        
        assert "Nessun esercizio specificato" in table_html
        assert "<table>" not in table_html
    
    def test_format_for_print_complete(self, sample_workout_plan):
        """Test formattazione per stampa"""
        print_text = WorkoutFormatter.format_for_print(sample_workout_plan)
        
        assert isinstance(print_text, str)
        assert "=" * 60 in print_text
        assert sample_workout_plan.title.upper() in print_text
        assert "PROFILO UTENTE:" in print_text
        assert "LUNEDÌ - CORPO COMPLETO" in print_text
        assert "RISCALDAMENTO:" in print_text
        assert "ESERCIZI:" in print_text
        assert "1. Squat" in print_text
        assert "2. Push-up" in print_text
        assert "Serie: 3" in print_text
        assert "NOTE IMPORTANTI:" in print_text
    
    def test_format_for_print_exercise_details(self, sample_workout_plan):
        """Test dettagli esercizi nella stampa"""
        print_text = WorkoutFormatter.format_for_print(sample_workout_plan)
        
        # Verifica formato esercizi
        assert "Ripetizioni: 12-15" in print_text
        assert "Recupero: 90 sec" in print_text
        assert "Peso: Peso corporeo" in print_text
        assert "Note: Mantieni schiena dritta" in print_text
        assert "Muscoli: quadricipiti, glutei" in print_text
    
    def test_format_summary_complete(self, sample_workout_plan):
        """Test creazione riassunto scheda"""
        summary = WorkoutFormatter.format_summary(sample_workout_plan)
        
        assert isinstance(summary, dict)
        assert summary["total_days"] == 1
        assert summary["total_exercises"] == 2
        assert summary["total_sets"] == 6  # 3 + 3
        assert "quadricipiti" in summary["muscle_groups_covered"]
        assert "glutei" in summary["muscle_groups_covered"]
        assert "pettorali" in summary["muscle_groups_covered"]
        assert summary["estimated_weekly_duration"] == 45
        assert summary["experience_level"] == "principiante"
        assert "fitness_generale" in summary["primary_goals"]
        assert summary["has_nutrition_guide"] is True
        assert summary["has_progression_plan"] is True
    
    def test_format_summary_empty_workout(self):
        """Test riassunto scheda vuota"""
        empty_workout = WorkoutPlan(
            id="empty",
            title="Empty Workout",
            user_profile=UserProfile(
                experience_level=ExperienceLevel.BEGINNER,
                goals=[WorkoutGoal.GENERAL_FITNESS],
                available_days=3
            ),
            workout_days=[]
        )
        
        summary = WorkoutFormatter.format_summary(empty_workout)
        
        assert summary["total_days"] == 0
        assert summary["total_exercises"] == 0
        assert summary["total_sets"] == 0
        assert summary["muscle_groups_covered"] == []
        assert summary["estimated_weekly_duration"] == 0
        assert summary["has_nutrition_guide"] is False
        assert summary["has_progression_plan"] is False
    
    def test_format_for_chat_minimal_workout(self):
        """Test formattazione scheda minimale"""
        minimal_workout = WorkoutPlan(
            id="minimal",
            title="Minimal Workout", 
            user_profile=UserProfile(
                experience_level=ExperienceLevel.BEGINNER,
                goals=[WorkoutGoal.GENERAL_FITNESS],
                available_days=1
            ),
            workout_days=[
                WorkoutDay(
                    day="Lunedì",
                    focus="Test",
                    exercises=[
                        Exercise(name="Test Exercise", sets=1, reps="1", rest="1 min")
                    ]
                )
            ]
        )
        
        formatted = WorkoutFormatter.format_for_chat(minimal_workout)
        
        assert "Minimal Workout" in formatted
        assert "Lunedì" in formatted
        assert "Test Exercise" in formatted
        assert '<div class="workout-card">' in formatted
    
    def test_format_for_chat_no_optional_sections(self):
        """Test formattazione senza sezioni opzionali"""
        workout_no_optional = WorkoutPlan(
            id="no-optional",
            title="No Optional Sections",
            user_profile=UserProfile(
                experience_level=ExperienceLevel.BEGINNER,
                goals=[WorkoutGoal.GENERAL_FITNESS],
                available_days=1
            ),
            workout_days=[
                WorkoutDay(
                    day="Lunedì",
                    focus="Test",
                    exercises=[Exercise(name="Test", sets=1, reps="1", rest="1 min")]
                )
            ],
            nutrition=None,
            progression=None,
            general_notes=[]
        )
        
        formatted = WorkoutFormatter.format_for_chat(workout_no_optional)
        
        # Sezioni opzionali non dovrebbero essere presenti
        assert "🥗 Linee Guida Nutrizionali" not in formatted
        assert "📈 Piano di Progressione" not in formatted
        assert "📝 Note Importanti" not in formatted
    
    def test_format_for_chat_with_warm_up_cool_down(self):
        """Test formattazione con riscaldamento e defaticamento"""
        workout_with_warmup = WorkoutPlan(
            id="warmup-test",
            title="Warmup Test",
            user_profile=UserProfile(
                experience_level=ExperienceLevel.BEGINNER,
                goals=[WorkoutGoal.GENERAL_FITNESS],
                available_days=1
            ),
            workout_days=[
                WorkoutDay(
                    day="Lunedì",
                    focus="Test",
                    warm_up=["Camminata 5 min", "Mobilità spalle"],
                    exercises=[Exercise(name="Test", sets=1, reps="1", rest="1 min")],
                    cool_down=["Stretching statico", "Respirazione profonda"]
                )
            ]
        )
        
        formatted = WorkoutFormatter.format_for_chat(workout_with_warmup)
        
        assert "🔥 Riscaldamento" in formatted
        assert "Camminata 5 min" in formatted
        assert "Mobilità spalle" in formatted
        assert "🧘 Defaticamento" in formatted
        assert "Stretching statico" in formatted
        assert "Respirazione profonda" in formatted
    
    def test_format_duration_display(self):
        """Test visualizzazione durata sessione"""
        workout_with_duration = WorkoutPlan(
            id="duration-test",
            title="Duration Test",
            user_profile=UserProfile(
                experience_level=ExperienceLevel.BEGINNER,
                goals=[WorkoutGoal.GENERAL_FITNESS],
                available_days=1
            ),
            workout_days=[
                WorkoutDay(
                    day="Lunedì",
                    focus="Test",
                    exercises=[Exercise(name="Test", sets=1, reps="1", rest="1 min")],
                    duration_minutes=75
                )
            ]
        )
        
        formatted = WorkoutFormatter.format_for_chat(workout_with_duration)
        
        assert "⏱️ Durata stimata: 75 minuti" in formatted
