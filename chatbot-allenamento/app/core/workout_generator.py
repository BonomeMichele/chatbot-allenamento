"""
Generatore di schede allenamento
"""

import logging
import json
from typing import Dict, Any, List, Optional
from app.models.workout import (
    WorkoutPlan, WorkoutDay, Exercise, UserProfile, 
    NutritionGuidelines, ProgressionPlan, ExperienceLevel, WorkoutGoal
)
from app.core.llm_manager import LLMManager
from app.core.rag_engine import RAGEngine
from app.utils.prompt_templates import PromptTemplates
from app.core.error_handler import ChatbotException

logger = logging.getLogger(__name__)

class WorkoutGenerator:
    """Generatore intelligente di schede di allenamento"""
    
    def __init__(self, llm_manager: LLMManager, rag_engine: RAGEngine):
        self.llm_manager = llm_manager
        self.rag_engine = rag_engine
        self.prompt_templates = PromptTemplates()
    
    async def generate_complete_workout(
        self, 
        user_profile: UserProfile, 
        user_input: str
    ) -> WorkoutPlan:
        """
        Genera una scheda di allenamento completa
        
        Args:
            user_profile: Profilo dell'utente
            user_input: Input originale dell'utente
            
        Returns:
            Scheda di allenamento completa
        """
        try:
            # Recupera contesto rilevante
            context, sources = await self._get_relevant_context(user_profile)
            
            # Genera la scheda base
            workout_structure = await self._generate_workout_structure(
                user_profile, user_input, context
            )
            
            # Genera esercizi dettagliati
            workout_days = await self._generate_detailed_exercises(
                workout_structure, user_profile, context
            )
            
            # Genera linee guida nutrizionali
            nutrition = await self._generate_nutrition_guidelines(user_profile, context)
            
            # Genera piano di progressione
            progression = await self._generate_progression_plan(user_profile, context)
            
            # Assembla la scheda finale
            workout_plan = self._assemble_workout_plan(
                user_profile=user_profile,
                workout_days=workout_days,
                nutrition=nutrition,
                progression=progression,
                sources=sources
            )
            
            logger.info(f"Scheda generata: {len(workout_days)} giorni, {self._count_exercises(workout_days)} esercizi")
            return workout_plan
            
        except Exception as e:
            logger.error(f"Errore nella generazione scheda: {e}")
            raise ChatbotException(f"Errore nella generazione della scheda: {str(e)}")
    
    async def _get_relevant_context(self, user_profile: UserProfile) -> tuple[str, List[str]]:
        """Recupera contesto rilevante per il profilo utente"""
        # Costruisci query basata sul profilo
        query_parts = []
        
        # Livello esperienza
        query_parts.append(f"allenamento {user_profile.experience_level.value}")
        
        # Obiettivi
        goals_str = " ".join([goal.value for goal in user_profile.goals])
        query_parts.append(goals_str)
        
        # Giorni disponibili
        if user_profile.available_days <= 3:
            query_parts.append("corpo completo full body")
        elif user_profile.available_days >= 5:
            query_parts.append("split routine")
        else:
            query_parts.append("upper lower")
        
        # Limitazioni
        if user_profile.injuries:
            query_parts.extend(user_profile.injuries)
        
        query = " ".join(query_parts)
        return await self.rag_engine.retrieve_context(query)
    
    async def _generate_workout_structure(
        self, 
        user_profile: UserProfile, 
        user_input: str, 
        context: str
    ) -> Dict[str, Any]:
        """Genera la struttura base della scheda"""
        
        structure_prompt = f"""
Basandoti sul contesto fornito, crea la STRUTTURA di una scheda di allenamento.

PROFILO UTENTE:
- Livello: {user_profile.experience_level.value}
- Obiettivi: {', '.join([g.value for g in user_profile.goals])}
- Giorni disponibili: {user_profile.available_days}
- Età: {user_profile.age or 'Non specificata'}
- Limitazioni: {', '.join(user_profile.injuries) if user_profile.injuries else 'Nessuna'}

CONTESTO DOCUMENTALE:
{context}

RICHIESTA ORIGINALE:
{user_input}

Restituisci SOLO un JSON con questa struttura:
{{
    "title": "Titolo della scheda",
    "split_type": "full_body|upper_lower|push_pull_legs|body_part_split",
    "days_structure": [
        {{
            "day": "Lunedì",
            "focus": "Descrizione focus del giorno",
            "muscle_groups": ["gruppo1", "gruppo2"],
            "workout_type": "strength|hypertrophy|endurance|mixed"
        }}
    ],
    "session_duration": 60,
    "weekly_volume": "alto|medio|basso"
}}
"""
        
        response = await self.llm_manager.generate_response(
            messages=[{"role": "user", "content": structure_prompt}],
            system_prompt="Sei un esperto programmatore di allenamenti. Rispondi SOLO con JSON valido.",
            temperature=0.2
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Risposta struttura non in JSON, uso struttura di default")
            return self._get_default_structure(user_profile)
    
    async def _generate_detailed_exercises(
        self, 
        structure: Dict[str, Any], 
        user_profile: UserProfile, 
        context: str
    ) -> List[WorkoutDay]:
        """Genera esercizi dettagliati per ogni giorno"""
        
        workout_days = []
        
        for day_info in structure.get("days_structure", []):
            exercises_prompt = f"""
Basandoti sul contesto documentale, crea gli ESERCIZI per questo giorno di allenamento:

GIORNO: {day_info['day']} - {day_info['focus']}
GRUPPI MUSCOLARI: {', '.join(day_info['muscle_groups'])}
TIPO ALLENAMENTO: {day_info['workout_type']}

PROFILO UTENTE:
- Livello: {user_profile.experience_level.value}
- Obiettivi: {', '.join([g.value for g in user_profile.goals])}
- Attrezzature: {', '.join(user_profile.equipment) if user_profile.equipment else 'Standard palestra'}

CONTESTO:
{context}

Restituisci JSON con questa struttura:
{{
    "warm_up": ["esercizio1", "esercizio2"],
    "exercises": [
        {{
            "name": "Nome esercizio",
            "sets": 3,
            "reps": "8-12",
            "rest": "90 sec",
            "weight": "Indicazioni peso",
            "notes": "Note tecniche",
            "muscle_groups": ["muscolo1", "muscolo2"]
        }}
    ],
    "cool_down": ["defaticamento1", "defaticamento2"]
}}
"""
            
            response = await self.llm_manager.generate_response(
                messages=[{"role": "user", "content": exercises_prompt}],
                system_prompt="Sei un personal trainer esperto. Crea esercizi sicuri e appropriati. Rispondi SOLO con JSON.",
                temperature=0.3
            )
            
            try:
                day_data = json.loads(response)
                
                # Converti in oggetti Exercise
                exercises = []
                for ex_data in day_data.get("exercises", []):
                    exercise = Exercise(
                        name=ex_data.get("name", "Esercizio"),
                        sets=ex_data.get("sets", 3),
                        reps=ex_data.get("reps", "10-12"),
                        rest=ex_data.get("rest", "60 sec"),
                        weight=ex_data.get("weight"),
                        notes=ex_data.get("notes"),
                        muscle_groups=ex_data.get("muscle_groups", [])
                    )
                    exercises.append(exercise)
                
                workout_day = WorkoutDay(
                    day=day_info["day"],
                    focus=day_info["focus"],
                    warm_up=day_data.get("warm_up", []),
                    exercises=exercises,
                    cool_down=day_data.get("cool_down", []),
                    duration_minutes=structure.get("session_duration", 60)
                )
                
                workout_days.append(workout_day)
                
            except json.JSONDecodeError:
                logger.warning(f"Errore parsing esercizi per {day_info['day']}, uso default")
                workout_day = self._get_default_day(day_info, user_profile)
                workout_days.append(workout_day)
        
        return workout_days
    
    async def _generate_nutrition_guidelines(
        self, 
        user_profile: UserProfile, 
        context: str
    ) -> Optional[NutritionGuidelines]:
        """Genera linee guida nutrizionali"""
        
        if WorkoutGoal.WEIGHT_LOSS not in user_profile.goals and \
           WorkoutGoal.HYPERTROPHY not in user_profile.goals:
            return None
        
        nutrition_prompt = f"""
Basandoti sul contesto, crea linee guida nutrizionali GENERALI per:

PROFILO:
- Età: {user_profile.age or 'Non specificata'}
- Obiettivi: {', '.join([g.value for g in user_profile.goals])}
- Giorni allenamento: {user_profile.available_days}

CONTESTO:
{context}

Restituisci JSON:
{{
    "calories_estimate": "Range calorico stimato",
    "protein_grams": "Grammi proteine consigliati", 
    "meal_timing": ["timing1", "timing2"],
    "hydration": "Consigli idratazione",
    "supplements": ["integratore1", "integratore2"]
}}

IMPORTANTE: Fornisci solo linee guida generali, NON piani alimentari specifici.
"""
        
        try:
            response = await self.llm_manager.generate_response(
                messages=[{"role": "user", "content": nutrition_prompt}],
                system_prompt=self.prompt_templates.get_nutrition_advice_prompt(),
                temperature=0.2
            )
            
            nutrition_data = json.loads(response)
            
            return NutritionGuidelines(
                calories_estimate=nutrition_data.get("calories_estimate"),
                protein_grams=nutrition_data.get("protein_grams"),
                meal_timing=nutrition_data.get("meal_timing", []),
                hydration=nutrition_data.get("hydration"),
                supplements=nutrition_data.get("supplements", [])
            )
            
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Errore generazione nutrizione: {e}")
            return None
    
    async def _generate_progression_plan(
        self, 
        user_profile: UserProfile, 
        context: str
    ) -> Optional[ProgressionPlan]:
        """Genera piano di progressione"""
        
        progression_prompt = f"""
Crea un piano di progressione di 6 settimane per:

PROFILO:
- Livello: {user_profile.experience_level.value}
- Obiettivi: {', '.join([g.value for g in user_profile.goals])}

CONTESTO:
{context}

Restituisci JSON:
{{
    "week_1_2": "Descrizione settimane 1-2",
    "week_3_4": "Descrizione settimane 3-4", 
    "week_5_6": "Descrizione settimane 5-6",
    "deload_week": "Descrizione settimana scarico",
    "progression_notes": ["nota1", "nota2"]
}}
"""
        
        try:
            response = await self.llm_manager.generate_response(
                messages=[{"role": "user", "content": progression_prompt}],
                system_prompt="Crea progressioni graduali e sicure. Rispondi SOLO con JSON.",
                temperature=0.2
            )
            
            prog_data = json.loads(response)
            
            return ProgressionPlan(
                week_1_2=prog_data.get("week_1_2", ""),
                week_3_4=prog_data.get("week_3_4", ""),
                week_5_6=prog_data.get("week_5_6"),
                deload_week=prog_data.get("deload_week"),
                progression_notes=prog_data.get("progression_notes", [])
            )
            
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Errore generazione progressione: {e}")
            return self._get_default_progression(user_profile)
    
    def _assemble_workout_plan(
        self,
        user_profile: UserProfile,
        workout_days: List[WorkoutDay],
        nutrition: Optional[NutritionGuidelines],
        progression: Optional[ProgressionPlan],
        sources: List[str]
    ) -> WorkoutPlan:
        """Assembla la scheda finale"""
        
        import uuid
        
        # Genera titolo basato sul profilo
        title = self._generate_title(user_profile)
        
        # Note generali
        general_notes = self._generate_general_notes(user_profile)
        
        return WorkoutPlan(
            id=str(uuid.uuid4()),
            title=title,
            user_profile=user_profile,
            workout_days=workout_days,
            nutrition=nutrition,
            progression=progression,
            general_notes=general_notes,
            sources=sources
        )
    
    def _generate_title(self, user_profile: UserProfile) -> str:
        """Genera titolo per la scheda"""
        level_map = {
            ExperienceLevel.BEGINNER: "Principiante",
            ExperienceLevel.INTERMEDIATE: "Intermedio", 
            ExperienceLevel.ADVANCED: "Avanzato"
        }
        
        level = level_map.get(user_profile.experience_level, "Personalizzata")
        
        if len(user_profile.goals) == 1:
            goal = user_profile.goals[0]
            goal_map = {
                WorkoutGoal.STRENGTH: "Forza",
                WorkoutGoal.HYPERTROPHY: "Massa",
                WorkoutGoal.ENDURANCE: "Resistenza",
                WorkoutGoal.WEIGHT_LOSS: "Dimagrimento",
                WorkoutGoal.GENERAL_FITNESS: "Fitness"
            }
            goal_name = goal_map.get(goal, "Fitness")
            return f"Scheda {level} - {goal_name}"
        
        return f"Scheda {level} - {user_profile.available_days} giorni"
    
    def _generate_general_notes(self, user_profile: UserProfile) -> List[str]:
        """Genera note generali basate sul profilo"""
        notes = [
            "Inizia sempre con un riscaldamento adeguato di 5-10 minuti",
            "Mantieni sempre la corretta esecuzione tecnica",
            "Idratati adeguatamente durante l'allenamento",
            "Riposa 7-8 ore per notte per ottimizzare il recupero"
        ]
        
        if user_profile.experience_level == ExperienceLevel.BEGINNER:
            notes.extend([
                "Come principiante, concentrati prima sulla tecnica poi sull'intensità",
                "Non esitare a chiedere aiuto per imparare gli esercizi",
                "Progredisci gradualmente: meglio essere conservativi"
            ])
        
        if user_profile.injuries:
            notes.append("Rispetta sempre le limitazioni dovute a infortuni passati")
        
        if WorkoutGoal.STRENGTH in user_profile.goals:
            notes.append("Per la forza, concentrati su carichi elevati e recuperi completi")
        
        return notes
    
    def _get_default_structure(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Struttura di default in caso di errore"""
        if user_profile.available_days <= 3:
            return {
                "title": f"Scheda {user_profile.experience_level.value.title()}",
                "split_type": "full_body",
                "days_structure": [
                    {
                        "day": "Lunedì",
                        "focus": "Corpo completo A",
                        "muscle_groups": ["petto", "schiena", "gambe"],
                        "workout_type": "mixed"
                    },
                    {
                        "day": "Mercoledì", 
                        "focus": "Corpo completo B",
                        "muscle_groups": ["spalle", "braccia", "core"],
                        "workout_type": "mixed"
                    },
                    {
                        "day": "Venerdì",
                        "focus": "Corpo completo C", 
                        "muscle_groups": ["petto", "schiena", "gambe"],
                        "workout_type": "mixed"
                    }
                ][:user_profile.available_days],
                "session_duration": 60,
                "weekly_volume": "medio"
            }
        else:
            return {
                "title": f"Scheda {user_profile.experience_level.value.title()}",
                "split_type": "upper_lower",
                "days_structure": [
                    {
                        "day": "Lunedì",
                        "focus": "Parte superiore",
                        "muscle_groups": ["petto", "schiena", "spalle", "braccia"],
                        "workout_type": "mixed"
                    },
                    {
                        "day": "Martedì",
                        "focus": "Parte inferiore",
                        "muscle_groups": ["quadricipiti", "femorali", "glutei", "polpacci"],
                        "workout_type": "mixed" 
                    }
                ],
                "session_duration": 60,
                "weekly_volume": "medio"
            }
    
    def _get_default_day(self, day_info: Dict[str, Any], user_profile: UserProfile) -> WorkoutDay:
        """Giorno di default in caso di errore"""
        # Esercizi base per principianti
        if user_profile.experience_level == ExperienceLevel.BEGINNER:
            exercises = [
                Exercise(name="Squat assistito", sets=3, reps="12-15", rest="90 sec"),
                Exercise(name="Push-up (modificato)", sets=3, reps="8-12", rest="60 sec"),
                Exercise(name="Plank", sets=3, reps="30 sec", rest="60 sec")
            ]
        else:
            exercises = [
                Exercise(name="Squat con bilanciere", sets=4, reps="8-10", rest="2 min"),
                Exercise(name="Panca piana", sets=4, reps="8-10", rest="2 min"),
                Exercise(name="Rematore", sets=4, reps="8-10", rest="90 sec")
            ]
        
        return WorkoutDay(
            day=day_info["day"],
            focus=day_info["focus"],
            warm_up=["Riscaldamento articolare", "Attivazione muscolare"],
            exercises=exercises,
            cool_down=["Stretching statico", "Respirazione profonda"],
            duration_minutes=60
        )
    
    def _get_default_progression(self, user_profile: UserProfile) -> ProgressionPlan:
        """Progressione di default"""
        if user_profile.experience_level == ExperienceLevel.BEGINNER:
            return ProgressionPlan(
                week_1_2="Focus sulla tecnica e apprendimento movimenti",
                week_3_4="Aumento graduale delle ripetizioni",
                week_5_6="Introduzione di carichi leggeri",
                deload_week="Riduci il volume del 40% per recuperare",
                progression_notes=[
                    "Progredisci solo quando la tecnica è perfetta",
                    "Ascolta sempre il tuo corpo"
                ]
            )
        else:
            return ProgressionPlan(
                week_1_2="Adattamento al nuovo programma", 
                week_3_4="Aumento intensità e volume",
                week_5_6="Picco di intensità",
                deload_week="Settimana di scarico attivo",
                progression_notes=[
                    "Monitora i progressi settimanalmente",
                    "Adatta i carichi in base alle sensazioni"
                ]
            )
    
    def _count_exercises(self, workout_days: List[WorkoutDay]) -> int:
        """Conta il numero totale di esercizi"""
        return sum(len(day.exercises) for day in workout_days)
