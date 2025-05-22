"""
Modelli dati per le schede di allenamento
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class ExperienceLevel(str, Enum):
    """Livelli di esperienza"""
    BEGINNER = "principiante"
    INTERMEDIATE = "intermedio"
    ADVANCED = "avanzato"

class WorkoutGoal(str, Enum):
    """Obiettivi dell'allenamento"""
    STRENGTH = "forza"
    HYPERTROPHY = "ipertrofia"
    ENDURANCE = "resistenza"
    WEIGHT_LOSS = "dimagrimento"
    GENERAL_FITNESS = "fitness_generale"
    REHABILITATION = "riabilitazione"

class Gender(str, Enum):
    """Genere"""
    MALE = "maschio"
    FEMALE = "femmina"
    OTHER = "altro"

class Exercise(BaseModel):
    """Modello per un singolo esercizio"""
    name: str = Field(..., description="Nome dell'esercizio")
    sets: int = Field(..., description="Numero di serie")
    reps: str = Field(..., description="Numero di ripetizioni (può includere range)")
    rest: str = Field(..., description="Tempo di recupero")
    weight: Optional[str] = Field(default=None, description="Peso consigliato")
    notes: Optional[str] = Field(default=None, description="Note tecniche")
    muscle_groups: List[str] = Field(default_factory=list, description="Gruppi muscolari coinvolti")

class WorkoutDay(BaseModel):
    """Modello per un giorno di allenamento"""
    day: str = Field(..., description="Giorno della settimana")
    focus: str = Field(..., description="Focus del giorno (es. 'Petto e Tricipiti')")
    warm_up: List[str] = Field(default_factory=list, description="Esercizi di riscaldamento")
    exercises: List[Exercise] = Field(default_factory=list, description="Esercizi principali")
    cool_down: List[str] = Field(default_factory=list, description="Esercizi di defaticamento")
    duration_minutes: Optional[int] = Field(default=None, description="Durata stimata in minuti")

class NutritionGuidelines(BaseModel):
    """Linee guida nutrizionali"""
    calories_estimate: Optional[str] = Field(default=None, description="Stima calorie giornaliere")
    protein_grams: Optional[str] = Field(default=None, description="Grammi di proteine consigliati")
    meal_timing: List[str] = Field(default_factory=list, description="Timing dei pasti")
    hydration: Optional[str] = Field(default=None, description="Consigli per l'idratazione")
    supplements: List[str] = Field(default_factory=list, description="Integratori suggeriti")

class ProgressionPlan(BaseModel):
    """Piano di progressione"""
    week_1_2: str = Field(..., description="Settimane 1-2")
    week_3_4: str = Field(..., description="Settimane 3-4")
    week_5_6: Optional[str] = Field(default=None, description="Settimane 5-6")
    deload_week: Optional[str] = Field(default=None, description="Settimana di scarico")
    progression_notes: List[str] = Field(default_factory=list, description="Note sulla progressione")

class UserProfile(BaseModel):
    """Profilo dell'utente per la generazione della scheda"""
    age: Optional[int] = Field(default=None, description="Età")
    gender: Optional[Gender] = Field(default=None, description="Genere")
    experience_level: ExperienceLevel = Field(..., description="Livello di esperienza")
    goals: List[WorkoutGoal] = Field(..., description="Obiettivi dell'allenamento")
    available_days: int = Field(..., description="Giorni disponibili per l'allenamento")
    session_duration: Optional[int] = Field(default=None, description="Durata sessione in minuti")
    injuries: List[str] = Field(default_factory=list, description="Infortuni o limitazioni")
    equipment: List[str] = Field(default_factory=list, description="Attrezzature disponibili")
    preferences: List[str] = Field(default_factory=list, description="Preferenze personali")

class WorkoutPlan(BaseModel):
    """Modello per una scheda di allenamento completa"""
    id: str = Field(..., description="ID univoco della scheda")
    title: str = Field(..., description="Titolo della scheda")
    user_profile: UserProfile = Field(..., description="Profilo dell'utente")
    workout_days: List[WorkoutDay] = Field(..., description="Giorni di allenamento")
    nutrition: Optional[NutritionGuidelines] = Field(default=None, description="Linee guida nutrizionali")
    progression: Optional[ProgressionPlan] = Field(default=None, description="Piano di progressione")
    general_notes: List[str] = Field(default_factory=list, description="Note generali")
    created_at: datetime = Field(default_factory=datetime.now, description="Data di creazione")
    sources: List[str] = Field(default_factory=list, description="Fonti utilizzate")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadati aggiuntivi")
    
    def get_total_exercises(self) -> int:
        """Ottiene il numero totale di esercizi nella scheda"""
        return sum(len(day.exercises) for day in self.workout_days)
    
    def get_weekly_volume(self) -> int:
        """Ottiene il volume settimanale totale (serie)"""
        return sum(
            sum(exercise.sets for exercise in day.exercises)
            for day in self.workout_days
        )
    
    def get_muscle_groups_covered(self) -> List[str]:
        """Ottiene tutti i gruppi muscolari coperti nella scheda"""
        muscle_groups = set()
        for day in self.workout_days:
            for exercise in day.exercises:
                muscle_groups.update(exercise.muscle_groups)
        return list(muscle_groups)
