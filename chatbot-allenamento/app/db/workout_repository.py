"""
Repository per operazioni su schede allenamento
"""

import logging
from typing import List, Optional, Dict, Any
from app.db.file_storage import FileStorage
from app.models.workout import WorkoutPlan
from app.core.error_handler import StorageException

logger = logging.getLogger(__name__)

class WorkoutRepository:
    """Repository per gestione schede allenamento"""
    
    def __init__(self, storage: FileStorage):
        self.storage = storage
    
    async def save(self, workout: WorkoutPlan) -> None:
        """
        Salva una scheda di allenamento
        
        Args:
            workout: Scheda da salvare
        """
        try:
            workout_data = workout.model_dump()
            self.storage.save_workout(workout_data)
            logger.info(f"Scheda {workout.id} salvata nel repository")
            
        except Exception as e:
            logger.error(f"Errore nel salvataggio scheda {workout.id}: {e}")
            raise StorageException(f"Errore nel salvataggio scheda: {str(e)}")
    
    async def find_by_id(self, workout_id: str) -> Optional[WorkoutPlan]:
        """
        Trova una scheda per ID
        
        Args:
            workout_id: ID della scheda
            
        Returns:
            Scheda trovata o None
        """
        try:
            workout_data = self.storage.load_workout(workout_id)
            if not workout_data:
                return None
            
            # Converti in oggetto WorkoutPlan
            workout = WorkoutPlan(**workout_data)
            return workout
            
        except Exception as e:
            logger.error(f"Errore nel recupero scheda {workout_id}: {e}")
            return None
    
    async def find_all(self, limit: Optional[int] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Trova tutte le schede
        
        Args:
            limit: Numero massimo di schede
            user_id: Filtra per utente specifico (se implementato)
            
        Returns:
            Lista delle schede
        """
        try:
            workouts = self.storage.list_workouts(limit=limit)
            
            # TODO: Implementare filtro per user_id quando aggiunto al modello WorkoutPlan
            
            return workouts
            
        except Exception as e:
            logger.error(f"Errore nel recupero lista schede: {e}")
            raise StorageException(f"Errore nel recupero lista schede: {str(e)}")
    
    async def delete(self, workout_id: str) -> bool:
        """
        Elimina una scheda
        
        Args:
            workout_id: ID della scheda da eliminare
            
        Returns:
            True se eliminata con successo
        """
        try:
            result = self.storage.delete_workout(workout_id)
            if result:
                logger.info(f"Scheda {workout_id} eliminata dal repository")
            return result
            
        except Exception as e:
            logger.error(f"Errore nell'eliminazione scheda {workout_id}: {e}")
            raise StorageException(f"Errore nell'eliminazione scheda: {str(e)}")
    
    async def count(self) -> int:
        """
        Conta il numero di schede
        
        Returns:
            Numero di schede
        """
        try:
            workouts = await self.find_all()
            return len(workouts)
            
        except Exception as e:
            logger.error(f"Errore nel conteggio schede: {e}")
            return 0
    
    async def find_by_goal(self, goal: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Trova schede per obiettivo specifico
        
        Args:
            goal: Obiettivo da cercare
            limit: Numero massimo di risultati
            
        Returns:
            Lista delle schede matching
        """
        try:
            all_workouts = await self.find_all()
            matching_workouts = []
            
            for workout_info in all_workouts:
                # Carica la scheda completa per verificare gli obiettivi
                workout = await self.find_by_id(workout_info['id'])
                if workout and any(g.value.lower() == goal.lower() for g in workout.user_profile.goals):
                    matching_workouts.append(workout_info)
                    
                    if limit and len(matching_workouts) >= limit:
                        break
            
            return matching_workouts
            
        except Exception as e:
            logger.error(f"Errore nella ricerca per obiettivo {goal}: {e}")
            return []
    
    async def find_by_experience_level(self, level: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Trova schede per livello di esperienza
        
        Args:
            level: Livello di esperienza
            limit: Numero massimo di risultati
            
        Returns:
            Lista delle schede matching
        """
        try:
            all_workouts = await self.find_all()
            matching_workouts = []
            
            for workout_info in all_workouts:
                workout = await self.find_by_id(workout_info['id'])
                if workout and workout.user_profile.experience_level.value.lower() == level.lower():
                    matching_workouts.append(workout_info)
                    
                    if limit and len(matching_workouts) >= limit:
                        break
            
            return matching_workouts
            
        except Exception as e:
            logger.error(f"Errore nella ricerca per livello {level}: {e}")
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Ottiene statistiche sulle schede
        
        Returns:
            Dizionario con statistiche
        """
        try:
            all_workouts = await self.find_all()
            
            if not all_workouts:
                return {
                    'total_workouts': 0,
                    'by_experience_level': {},
                    'by_goals': {},
                    'average_days': 0,
                    'average_exercises': 0
                }
            
            # Contatori
            by_experience = {}
            by_goals = {}
            total_days = 0
            total_exercises = 0
            
            for workout_info in all_workouts:
                workout = await self.find_by_id(workout_info['id'])
                if workout:
                    # Conta per livello esperienza
                    level = workout.user_profile.experience_level.value
                    by_experience[level] = by_experience.get(level, 0) + 1
                    
                    # Conta per obiettivi
                    for goal in workout.user_profile.goals:
                        by_goals[goal.value] = by_goals.get(goal.value, 0) + 1
                    
                    # Somma giorni ed esercizi
                    total_days += len(workout.workout_days)
                    total_exercises += sum(len(day.exercises) for day in workout.workout_days)
            
            return {
                'total_workouts': len(all_workouts),
                'by_experience_level': by_experience,
                'by_goals': by_goals,
                'average_days': round(total_days / len(all_workouts), 1) if all_workouts else 0,
                'average_exercises': round(total_exercises / len(all_workouts), 1) if all_workouts else 0
            }
            
        except Exception as e:
            logger.error(f"Errore nel calcolo statistiche: {e}")
            return {'error': str(e)}
