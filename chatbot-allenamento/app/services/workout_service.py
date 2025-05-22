"""
Servizio per generazione schede allenamento
"""

import logging
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from app.models.workout import WorkoutPlan, UserProfile, ExperienceLevel, WorkoutGoal, Gender
from app.db.file_storage import FileStorage
from app.core.llm_manager import LLMManager
from app.core.rag_engine import RAGEngine
from app.utils.prompt_templates import PromptTemplates
from app.core.error_handler import ChatbotException

logger = logging.getLogger(__name__)

class WorkoutService:
    """Servizio per la generazione di schede di allenamento"""
    
    def __init__(self, storage: FileStorage, llm_manager: LLMManager, rag_engine: RAGEngine):
        self.storage = storage
        self.llm_manager = llm_manager
        self.rag_engine = rag_engine
        self.prompt_templates = PromptTemplates()
    
    async def generate_workout_plan(self, user_input: str, chat_id: Optional[str] = None) -> WorkoutPlan:
        """
        Genera una scheda di allenamento personalizzata
        
        Args:
            user_input: Input dell'utente in linguaggio naturale
            chat_id: ID della chat associata (opzionale)
            
        Returns:
            Piano di allenamento generato
        """
        try:
            # Estrai il profilo utente dall'input
            user_profile_data = await self.llm_manager.extract_user_profile(user_input)
            user_profile = self._create_user_profile(user_profile_data)
            
            # Recupera contesto rilevante dal RAG
            context, sources = await self.rag_engine.retrieve_context(
                f"allenamento {' '.join(user_profile.goals)} {user_profile.experience_level.value}"
            )
            
            # Genera la scheda usando OpenAI
            workout_content = await self._generate_workout_content(
                user_input=user_input,
                user_profile=user_profile,
                context=context
            )
            
            # Crea l'oggetto WorkoutPlan
            workout_plan = self._create_workout_plan(
                workout_content=workout_content,
                user_profile=user_profile,
                sources=sources
            )
            
            # Salva la scheda
            await self.save_workout_plan(workout_plan)
            
            logger.info(f"Scheda generata con successo: {workout_plan.id}")
            return workout_plan
            
        except Exception as e:
            logger.error(f"Errore nella generazione della scheda: {e}")
            raise ChatbotException(f"Errore nella generazione della scheda: {str(e)}")
    
    def _create_user_profile(self, profile_data: Dict[str, Any]) -> UserProfile:
        """
        Crea un UserProfile dai dati estratti
        
        Args:
            profile_data: Dati del profilo estratti dal LLM
            
        Returns:
            Oggetto UserProfile
        """
        try:
            # Converti i dati in tipi appropriati
            experience_level = ExperienceLevel.BEGINNER
            if profile_data.get('experience_level'):
                try:
                    experience_level = ExperienceLevel(profile_data['experience_level'])
                except ValueError:
                    pass
            
            goals = []
            for goal_str in profile_data.get('goals', []):
                try:
                    goal = WorkoutGoal(goal_str)
                    goals.append(goal)
                except ValueError:
                    continue
            
            if not goals:
                goals = [WorkoutGoal.GENERAL_FITNESS]
            
            gender = None
            if profile_data.get('gender'):
                try:
                    gender = Gender(profile_data['gender'])
                except ValueError:
                    pass
            
            return UserProfile(
                age=profile_data.get('age'),
                gender=gender,
                experience_level=experience_level,
                goals=goals,
                available_days=profile_data.get('available_days', 3),
                session_duration=profile_data.get('session_duration'),
                injuries=profile_data.get('injuries', []),
                equipment=profile_data.get('equipment', []),
                preferences=profile_data.get('preferences', [])
            )
            
        except Exception as e:
            logger.warning(f"Errore nella creazione del profilo utente: {e}")
            # Profilo di default per principianti
            return UserProfile(
                experience_level=ExperienceLevel.BEGINNER,
                goals=[WorkoutGoal.GENERAL_FITNESS],
                available_days=3
            )
    
    async def _generate_workout_content(
        self,
        user_input: str,
        user_profile: UserProfile,
        context: str
    ) -> str:
        """
        Genera il contenuto della scheda usando OpenAI
        
        Args:
            user_input: Input originale dell'utente
            user_profile: Profilo dell'utente
            context: Contesto dal RAG
            
        Returns:
            Contenuto della scheda generata
        """
        system_prompt = self.prompt_templates.get_workout_generation_prompt()
        
        # Prepara le informazioni del profilo
        profile_info = f"""
Profilo dell'utente:
- Età: {user_profile.age or 'Non specificata'}
- Genere: {user_profile.gender.value if user_profile.gender else 'Non specificato'}
- Livello: {user_profile.experience_level.value}
- Obiettivi: {', '.join([goal.value for goal in user_profile.goals])}
- Giorni disponibili: {user_profile.available_days}
- Durata sessione: {user_profile.session_duration or 'Non specificata'} minuti
- Infortuni/limitazioni: {', '.join(user_profile.injuries) or 'Nessuno'}
- Attrezzature: {', '.join(user_profile.equipment) or 'Standard palestra'}
- Preferenze: {', '.join(user_profile.preferences) or 'Nessuna'}
"""
        
        return await self.llm_manager.generate_workout_response(
            user_input=f"{profile_info}\n\nRichiesta originale: {user_input}",
            context=context,
            system_prompt=system_prompt
        )
    
    def _create_workout_plan(
        self,
        workout_content: str,
        user_profile: UserProfile,
        sources: List[str]
    ) -> WorkoutPlan:
        """
        Crea un oggetto WorkoutPlan dal contenuto generato
        
        Args:
            workout_content: Contenuto della scheda
            user_profile: Profilo dell'utente
            sources: Fonti utilizzate
            
        Returns:
            Oggetto WorkoutPlan
        """
        workout_id = str(uuid.uuid4())
        
        # Prova a parsare il contenuto strutturato (se il LLM restituisce JSON)
        try:
            # Se il contenuto è JSON strutturato, usalo
            parsed_content = json.loads(workout_content)
            return self._parse_structured_workout(parsed_content, workout_id, user_profile, sources)
        except json.JSONDecodeError:
            # Se è testo libero, crea una scheda semplificata
            return self._parse_text_workout(workout_content, workout_id, user_profile, sources)
    
    def _parse_structured_workout(
        self,
        content: Dict[str, Any],
        workout_id: str,
        user_profile: UserProfile,
        sources: List[str]
    ) -> WorkoutPlan:
        """Parse workout da JSON strutturato"""
        from app.models.workout import WorkoutDay, Exercise, NutritionGuidelines, ProgressionPlan
        
        # Parse workout days
        workout_days = []
        for day_data in content.get('workout_days', []):
            exercises = []
            for ex_data in day_data.get('exercises', []):
                exercise = Exercise(
                    name=ex_data.get('name', ''),
                    sets=ex_data.get('sets', 3),
                    reps=ex_data.get('reps', '10-12'),
                    rest=ex_data.get('rest', '60-90 sec'),
                    weight=ex_data.get('weight'),
                    notes=ex_data.get('notes'),
                    muscle_groups=ex_data.get('muscle_groups', [])
                )
                exercises.append(exercise)
            
            workout_day = WorkoutDay(
                day=day_data.get('day', 'Giorno'),
                focus=day_data.get('focus', 'Allenamento'),
                warm_up=day_data.get('warm_up', []),
                exercises=exercises,
                cool_down=day_data.get('cool_down', []),
                duration_minutes=day_data.get('duration_minutes')
            )
            workout_days.append(workout_day)
        
        # Parse nutrition
        nutrition = None
        if content.get('nutrition'):
            nutrition_data = content['nutrition']
            nutrition = NutritionGuidelines(
                calories_estimate=nutrition_data.get('calories_estimate'),
                protein_grams=nutrition_data.get('protein_grams'),
                meal_timing=nutrition_data.get('meal_timing', []),
                hydration=nutrition_data.get('hydration'),
                supplements=nutrition_data.get('supplements', [])
            )
        
        # Parse progression
        progression = None
        if content.get('progression'):
            prog_data = content['progression']
            progression = ProgressionPlan(
                week_1_2=prog_data.get('week_1_2', ''),
                week_3_4=prog_data.get('week_3_4', ''),
                week_5_6=prog_data.get('week_5_6'),
                deload_week=prog_data.get('deload_week'),
                progression_notes=prog_data.get('progression_notes', [])
            )
        
        return WorkoutPlan(
            id=workout_id,
            title=content.get('title', f'Scheda per {user_profile.experience_level.value}'),
            user_profile=user_profile,
            workout_days=workout_days,
            nutrition=nutrition,
            progression=progression,
            general_notes=content.get('general_notes', []),
            sources=sources
        )
    
    def _parse_text_workout(
        self,
        content: str,
        workout_id: str,
        user_profile: UserProfile,
        sources: List[str]
    ) -> WorkoutPlan:
        """Parse workout da testo libero - versione semplificata"""
        from app.models.workout import WorkoutDay, Exercise
        
        # Crea una scheda base - in una implementazione reale potresti
        # usare regex o altre tecniche per parsare il testo
        title = f"Scheda {user_profile.experience_level.value.title()}"
        
        # Crea giorni di default basati sui giorni disponibili
        workout_days = []
        day_names = ["Lunedì", "Mercoledì", "Venerdì", "Martedì", "Giovedì", "Sabato", "Domenica"]
        
        for i in range(min(user_profile.available_days, 7)):
            day_name = day_names[i]
            
            # Esercizi di base per principianti
            if user_profile.experience_level == ExperienceLevel.BEGINNER:
                exercises = [
                    Exercise(name="Squat con peso corporeo", sets=3, reps="10-15", rest="60 sec"),
                    Exercise(name="Push-up", sets=3, reps="8-12", rest="60 sec"),
                    Exercise(name="Plank", sets=3, reps="30-45 sec", rest="60 sec")
                ]
            else:
                exercises = [
                    Exercise(name="Squat con bilanciere", sets=4, reps="8-10", rest="90 sec"),
                    Exercise(name="Panca piana", sets=4, reps="8-10", rest="90 sec"),
                    Exercise(name="Stacco da terra", sets=3, reps="6-8", rest="2 min")
                ]
            
            workout_day = WorkoutDay(
                day=day_name,
                focus="Corpo completo" if i < 3 else "Specifico",
                warm_up=["Camminata veloce 5 min", "Mobilità articolare"],
                exercises=exercises,
                cool_down=["Stretching statico", "Respirazione profonda"]
            )
            workout_days.append(workout_day)
        
        return WorkoutPlan(
            id=workout_id,
            title=title,
            user_profile=user_profile,
            workout_days=workout_days,
            general_notes=[
                "Inizia sempre con un riscaldamento adeguato",
                "Mantieni una corretta esecuzione tecnica",
                "Aumenta gradualmente l'intensità",
                "Consulta un trainer per dubbi sulla tecnica"
            ],
            sources=sources,
            metadata={"generated_from": "text_parsing", "content_preview": content[:200]}
        )
    
    async def save_workout_plan(self, workout_plan: WorkoutPlan) -> None:
        """
        Salva una scheda di allenamento
        
        Args:
            workout_plan: Schema da salvare
        """
        try:
            # Converti in dizionario per la serializzazione
            workout_data = workout_plan.model_dump()
            self.storage.save_workout(workout_data)
            
        except Exception as e:
            logger.error(f"Errore nel salvataggio della scheda {workout_plan.id}: {e}")
            raise ChatbotException(f"Errore nel salvataggio della scheda: {str(e)}")
    
    async def get_workout_plan(self, workout_id: str) -> Optional[WorkoutPlan]:
        """
        Recupera una scheda di allenamento
        
        Args:
            workout_id: ID della scheda
            
        Returns:
            Scheda trovata o None
        """
        try:
            workout_data = self.storage.load_workout(workout_id)
            if not workout_data:
                return None
            
            # Converti i dati in oggetto WorkoutPlan
            return WorkoutPlan(**workout_data)
            
        except Exception as e:
            logger.error(f"Errore nel recupero della scheda {workout_id}: {e}")
            return None
    
    async def list_workout_plans(self, limit: Optional[int] = None) -> List[dict]:
        """
        Lista tutte le schede di allenamento
        
        Args:
            limit: Numero massimo di schede da restituire
            
        Returns:
            Lista delle schede
        """
        try:
            return self.storage.list_workouts(limit=limit)
        except Exception as e:
            logger.error(f"Errore nell'elenco delle schede: {e}")
            raise ChatbotException(f"Errore nell'elenco delle schede: {str(e)}")
    
    async def delete_workout_plan(self, workout_id: str) -> bool:
        """
        Elimina una scheda di allenamento
        
        Args:
            workout_id: ID della scheda da eliminare
            
        Returns:
            True se eliminata con successo
        """
        try:
            return self.storage.delete_workout(workout_id)
        except Exception as e:
            logger.error(f"Errore nell'eliminazione della scheda {workout_id}: {e}")
            raise ChatbotException(f"Errore nell'eliminazione della scheda: {str(e)}")
    
    async def generate_workout_variations(self, base_workout_id: str, variation_type: str) -> WorkoutPlan:
        """
        Genera variazioni di una scheda esistente
        
        Args:
            base_workout_id: ID della scheda base
            variation_type: Tipo di variazione (easier, harder, different_focus, etc.)
            
        Returns:
            Nuova scheda con variazioni
        """
        try:
            base_workout = await self.get_workout_plan(base_workout_id)
            if not base_workout:
                raise ChatbotException("Scheda base non trovata")
            
            # Crea prompt per la variazione
            variation_prompt = f"""
Basandoti sulla seguente scheda di allenamento, crea una variazione "{variation_type}":

SCHEDA ORIGINALE:
{self.prompt_templates.format_workout_response(base_workout.model_dump())}

Crea una nuova scheda che sia una variazione di tipo "{variation_type}" mantenendo 
la stessa struttura ma modificando esercizi, intensità o focus secondo necessità.
"""
            
            # Recupera contesto
            context, sources = await self.rag_engine.retrieve_context(
                f"variazioni allenamento {variation_type}"
            )
            
            # Genera la variazione
            workout_content = await self.llm_manager.generate_workout_response(
                user_input=variation_prompt,
                context=context,
                system_prompt=self.prompt_templates.get_workout_generation_prompt()
            )
            
            # Crea la nuova scheda
            new_workout = self._create_workout_plan(
                workout_content=workout_content,
                user_profile=base_workout.user_profile,
                sources=sources
            )
            
            # Aggiorna il titolo
            new_workout.title = f"{base_workout.title} - Variazione {variation_type}"
            
            # Salva la nuova scheda
            await self.save_workout_plan(new_workout)
            
            return new_workout
            
        except Exception as e:
            logger.error(f"Errore nella generazione della variazione: {e}")
            raise ChatbotException(f"Errore nella generazione della variazione: {str(e)}")
    
    async def get_workout_recommendations(self, user_goals: List[str], experience_level: str) -> List[Dict[str, Any]]:
        """
        Ottiene raccomandazioni per schede basate su obiettivi e livello
        
        Args:
            user_goals: Lista degli obiettivi dell'utente
            experience_level: Livello di esperienza
            
        Returns:
            Lista di raccomandazioni
        """
        try:
            # Cerca nel RAG consigli per gli obiettivi specificati
            query = f"schede allenamento {' '.join(user_goals)} {experience_level}"
            context, sources = await self.rag_engine.retrieve_context(query)
            
            # Genera raccomandazioni
            recommendations_prompt = f"""
Basandoti sul contesto fornito, suggerisci 3-5 tipologie di schede di allenamento 
adatte per una persona con questi obiettivi: {', '.join(user_goals)}
e livello di esperienza: {experience_level}.

Per ogni raccomandazione includi:
- Nome della scheda
- Descrizione breve
- Giorni consigliati
- Focus principale
- Benefici attesi

Rispondi in formato JSON strutturato.
"""
            
            response = await self.llm_manager.generate_response(
                messages=[{"role": "user", "content": recommendations_prompt}],
                system_prompt="Sei un esperto di programmazione dell'allenamento. Fornisci consigli pratici e realistici.",
                temperature=0.3
            )
            
            try:
                recommendations = json.loads(response)
                return recommendations.get('recommendations', [])
            except json.JSONDecodeError:
                # Se non è JSON, restituisci una risposta di fallback
                return [{
                    "name": "Scheda Personalizzata",
                    "description": response[:200] + "...",
                    "days": 3,
                    "focus": "Adattato ai tuoi obiettivi",
                    "benefits": "Basato sulle linee guida professionali"
                }]
                
        except Exception as e:
            logger.error(f"Errore nelle raccomandazioni: {e}")
            return []
    
    def format_workout_for_display(self, workout_plan: WorkoutPlan) -> str:
        """
        Formatta una scheda per la visualizzazione nel chat
        
        Args:
            workout_plan: Scheda da formattare
            
        Returns:
            Testo formattato per la chat
        """
        return self.prompt_templates.format_workout_response(workout_plan.model_dump())
