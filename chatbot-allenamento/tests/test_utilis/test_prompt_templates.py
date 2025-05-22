"""
Test per PromptTemplates
"""

import pytest
from app.utils.prompt_templates import PromptTemplates

class TestPromptTemplates:
    """Test per i template di prompt"""
    
    @pytest.fixture
    def prompt_templates(self):
        """Fixture per PromptTemplates"""
        return PromptTemplates()
    
    def test_get_chat_system_prompt(self, prompt_templates):
        """Test prompt di sistema per chat"""
        prompt = prompt_templates.get_chat_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 100
        assert "assistente AI" in prompt.lower()
        assert "fitness" in prompt.lower()
        assert "italiano" in prompt.lower()
        assert "sicurezza" in prompt.lower()
    
    def test_get_workout_generation_prompt(self, prompt_templates):
        """Test prompt per generazione schede"""
        prompt = prompt_templates.get_workout_generation_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 200
        assert "personal trainer" in prompt.lower()
        assert "scheda" in prompt.lower()
        assert "sicurezza" in prompt.lower()
        assert "riscaldamento" in prompt.lower()
        assert "defaticamento" in prompt.lower()
        assert "serie" in prompt.lower()
        assert "ripetizioni" in prompt.lower()
    
    def test_get_technique_explanation_prompt(self, prompt_templates):
        """Test prompt per spiegazioni tecniche"""
        prompt = prompt_templates.get_technique_explanation_prompt()
        
        assert isinstance(prompt, str)
        assert "biomeccanica" in prompt.lower()
        assert "posizione di partenza" in prompt.lower()
        assert "esecuzione" in prompt.lower()
        assert "muscoli coinvolti" in prompt.lower()
        assert "errori comuni" in prompt.lower()
        assert "varianti" in prompt.lower()
        assert "precauzioni" in prompt.lower()
    
    def test_get_nutrition_advice_prompt(self, prompt_templates):
        """Test prompt per consigli nutrizionali"""
        prompt = prompt_templates.get_nutrition_advice_prompt()
        
        assert isinstance(prompt, str)
        assert "nutrizionista" in prompt.lower()
        assert "proteine" in prompt.lower()
        assert "carboidrati" in prompt.lower()
        assert "idratazione" in prompt.lower()
        assert "professionista" in prompt.lower()
    
    def test_get_user_profile_extraction_prompt(self, prompt_templates):
        """Test prompt per estrazione profilo utente"""
        prompt = prompt_templates.get_user_profile_extraction_prompt()
        
        assert isinstance(prompt, str)
        assert "JSON" in prompt
        assert "age" in prompt
        assert "gender" in prompt
        assert "experience_level" in prompt
        assert "goals" in prompt
        assert "available_days" in prompt
        assert "injuries" in prompt
        assert "equipment" in prompt
        assert "preferences" in prompt
    
    def test_get_contextual_prompt_general(self, prompt_templates):
        """Test prompt contestuale generale"""
        context = "Contesto di test sui pettorali"
        prompt = prompt_templates.get_contextual_prompt(context, "general")
        
        assert isinstance(prompt, str)
        assert context in prompt
        assert "CONTESTO DOCUMENTALE" in prompt
        assert "fonti" in prompt.lower()
    
    def test_get_contextual_prompt_beginner(self, prompt_templates):
        """Test prompt contestuale per principianti"""
        context = "Contesto per principianti"
        prompt = prompt_templates.get_contextual_prompt(context, "beginner")
        
        assert isinstance(prompt, str)
        assert context in prompt
        assert "principiante" in prompt.lower()
        assert "sicurezza" in prompt.lower()
        assert "gradualmente" in prompt.lower()
    
    def test_get_contextual_prompt_intermediate(self, prompt_templates):
        """Test prompt contestuale per intermedi"""
        context = "Contesto per intermedi"
        prompt = prompt_templates.get_contextual_prompt(context, "intermediate")
        
        assert isinstance(prompt, str)
        assert context in prompt
        assert "intermedia" in prompt.lower() or "esperienza" in prompt.lower()
        assert "tecniche" in prompt.lower()
    
    def test_get_contextual_prompt_advanced(self, prompt_templates):
        """Test prompt contestuale per avanzati"""
        context = "Contesto per avanzati"
        prompt = prompt_templates.get_contextual_prompt(context, "advanced")
        
        assert isinstance(prompt, str)
        assert context in prompt
        assert "avanzat" in prompt.lower()
        assert "periodizzazione" in prompt.lower() or "tecnic" in prompt.lower()
    
    def test_format_workout_response_complete(self, prompt_templates, sample_workout_data):
        """Test formattazione scheda completa"""
        formatted = prompt_templates.format_workout_response(sample_workout_data)
        
        assert isinstance(formatted, str)
        assert sample_workout_data["title"] in formatted
        assert "👤 Il Tuo Profilo" in formatted
        assert "📅" in formatted  # Emoji giorni
        assert "💪 Esercizi Principali" in formatted
        assert "🥗 Linee Guida Nutrizionali" in formatted
        assert "📈 Piano di Progressione" in formatted
        assert "📝 Note Importanti" in formatted
        assert "📚 Fonti" in formatted
    
    def test_format_workout_response_minimal(self, prompt_templates):
        """Test formattazione scheda con dati minimi"""
        minimal_data = {
            "title": "Scheda Minima",
            "user_profile": {
                "experience_level": "principiante",
                "goals": ["fitness_generale"],
                "available_days": 3
            },
            "workout_days": [
                {
                    "day": "Lunedì",
                    "focus": "Test",
                    "warm_up": [],
                    "exercises": [
                        {
                            "name": "Squat",
                            "sets": 3,
                            "reps": "10",
                            "rest": "60 sec"
                        }
                    ],
                    "cool_down": []
                }
            ],
            "nutrition": None,
            "progression": None,
            "general_notes": [],
            "sources": []
        }
        
        formatted = prompt_templates.format_workout_response(minimal_data)
        
        assert isinstance(formatted, str)
        assert "Scheda Minima" in formatted
        assert "Squat" in formatted
        assert "3" in formatted  # Sets
        assert "10" in formatted  # Reps
    
    def test_format_workout_response_with_table(self, prompt_templates):
        """Test formattazione con tabella esercizi"""
        workout_data = {
            "title": "Test Workout",
            "user_profile": {
                "experience_level": "principiante",
                "goals": ["fitness_generale"],
                "available_days": 3
            },
            "workout_days": [
                {
                    "day": "Lunedì",
                    "focus": "Test",
                    "exercises": [
                        {
                            "name": "Push-up",
                            "sets": 3,
                            "reps": "8-12",
                            "rest": "60 sec",
                            "weight": "Corpo libero",
                            "notes": "Mantieni corpo dritto"
                        },
                        {
                            "name": "Squat",
                            "sets": 4,
                            "reps": "12-15",
                            "rest": "90 sec",
                            "weight": None,
                            "notes": None
                        }
                    ]
                }
            ],
            "sources": []
        }
        
        formatted = prompt_templates.format_workout_response(workout_data)
        
        # Verifica presenza tabella
        assert "| Esercizio | Serie | Ripetizioni | Recupero |" in formatted
        assert "|-----------|-------|-------------|----------|" in formatted
        assert "| Push-up | 3 | 8-12 | 60 sec |" in formatted
        assert "| Squat | 4 | 12-15 | 90 sec |" in formatted
    
    def test_format_workout_response_with_nutrition(self, prompt_templates):
        """Test formattazione con sezione nutrizione"""
        workout_data = {
            "title": "Test",
            "user_profile": {"experience_level": "principiante", "goals": ["fitness_generale"], "available_days": 3},
            "workout_days": [],
            "nutrition": {
                "calories_estimate": "2000 kcal",
                "protein_grams": "100g",
                "meal_timing": ["Colazione abbondante", "Spuntino pre-workout"],
                "hydration": "2.5L",
                "supplements": ["Proteine", "Creatina"]
            },
            "sources": []
        }
        
        formatted = prompt_templates.format_workout_response(workout_data)
        
        assert "🥗 Linee Guida Nutrizionali" in formatted
        assert "2000 kcal" in formatted
        assert "100g" in formatted
        assert "Colazione abbondante" in formatted
        assert "2.5L" in formatted
        assert "Proteine" in formatted
        assert "Creatina" in formatted
    
    def test_format_workout_response_with_progression(self, prompt_templates):
        """Test formattazione con piano progressione"""
        workout_data = {
            "title": "Test",
            "user_profile": {"experience_level": "principiante", "goals": ["fitness_generale"], "available_days": 3},
            "workout_days": [],
            "progression": {
                "week_1_2": "Settimane iniziali",
                "week_3_4": "Settimane intermedie",
                "week_5_6": "Settimane avanzate",
                "deload_week": "Settimana scarico"
            },
            "sources": []
        }
        
        formatted = prompt_templates.format_workout_response(workout_data)
        
        assert "📈 Piano di Progressione" in formatted
        assert "Settimane 1-2" in formatted
        assert "Settimane iniziali" in formatted
        assert "Settimane 3-4" in formatted
        assert "Settimane intermedie" in formatted
        assert "Settimane 5-6" in formatted
        assert "Settimane avanzate" in formatted
    
    def test_format_workout_response_empty_sections(self, prompt_templates):
        """Test formattazione con sezioni vuote"""
        workout_data = {
            "title": "Test Empty",
            "user_profile": {"experience_level": "principiante", "goals": ["fitness_generale"], "available_days": 3},
            "workout_days": [],
            "nutrition": None,
            "progression": None,
            "general_notes": [],
            "sources": []
        }
        
        formatted = prompt_templates.format_workout_response(workout_data)
        
        # Sezioni vuote non dovrebbero apparire
        assert "🥗 Linee Guida Nutrizionali" not in formatted
        assert "📈 Piano di Progressione" not in formatted
        assert "📝 Note Importanti" not in formatted
        assert "📚 Fonti" not in formatted
        
        # Solo titolo e profilo dovrebbero essere presenti
        assert "Test Empty" in formatted
        assert "👤 Il Tuo Profilo" in formatted
    
    def test_all_prompts_are_strings(self, prompt_templates):
        """Test che tutti i prompt restituiscano stringhe non vuote"""
        methods = [
            'get_chat_system_prompt',
            'get_workout_generation_prompt', 
            'get_technique_explanation_prompt',
            'get_nutrition_advice_prompt',
            'get_user_profile_extraction_prompt'
        ]
        
        for method_name in methods:
            method = getattr(prompt_templates, method_name)
            result = method()
            
            assert isinstance(result, str), f"{method_name} deve restituire una stringa"
            assert len(result) > 0, f"{method_name} non può restituire stringa vuota"
            assert len(result) > 50, f"{method_name} deve restituire contenuto sostanziale"
    
    def test_contextual_prompt_with_empty_context(self, prompt_templates):
        """Test prompt contestuale con contesto vuoto"""
        prompt = prompt_templates.get_contextual_prompt("", "general")
        
        assert isinstance(prompt, str)
        assert "CONTESTO DOCUMENTALE" in prompt
        # Anche con contesto vuoto, deve restituire un prompt valido
